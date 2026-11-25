from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .cart import detalhes_carrinho, ler_carrinho
from .catalogo import filtrar_produtos
from .forms import PedidoForm
from .models import Pedido, Produto, Vendedor
from .precos import ZERO, calcular_descontos
from .services import ErroPedido, buscar_cupom, criar_pedido


def inicio(request):
    produtos = Produto.objects.filter(ativo=True, vendedor__ativo=True).select_related("vendedor")
    destaques = list(produtos.filter(destaque=True)[:4])
    if not destaques:
        destaques = list(produtos[:4])
    return render(request, "loja/inicio.html", {"destaques": destaques})


def catalogo(request):
    produtos = Produto.objects.filter(ativo=True, vendedor__ativo=True).select_related("vendedor")
    produtos, busca, categoria = filtrar_produtos(produtos, request.GET)
    vendedores = Vendedor.objects.filter(ativo=True, produtos__ativo=True).distinct()
    vendedor_id = request.GET.get("vendedor", "")
    vendedor = None
    if vendedor_id.isascii() and vendedor_id.isdecimal() and len(vendedor_id) <= 18:
        vendedor = vendedores.filter(pk=vendedor_id).first()
        if vendedor:
            produtos = produtos.filter(vendedor=vendedor)
    return render(request, "loja/catalogo.html", {
        "produtos": produtos,
        "categorias": Produto.Categoria.choices,
        "categoria_ativa": categoria,
        "busca": busca,
        "vendedores": vendedores,
        "vendedor_ativo": vendedor,
    })


def produto(request, vendedor_id, slug):
    item = get_object_or_404(
        Produto.objects.select_related("vendedor"),
        vendedor_id=vendedor_id, slug=slug, ativo=True, vendedor__ativo=True,
    )
    relacionados = Produto.objects.filter(
        ativo=True, vendedor__ativo=True, categoria=item.categoria
    ).exclude(pk=item.pk).select_related("vendedor")[:3]
    return render(request, "loja/produto.html", {"produto": item, "relacionados": relacionados})


def produto_legado(request, slug):
    produto = Produto.objects.filter(slug=slug, ativo=True, vendedor__ativo=True).order_by("pk").first()
    if produto is None:
        raise Http404
    return redirect(produto)


def carrinho(request):
    return render(request, "loja/carrinho.html", detalhes_carrinho(request))


def _quantidade(valor):
    try:
        quantidade = int(valor)
    except (TypeError, ValueError):
        return None
    return quantidade if 1 <= quantidade <= 99 else None


@require_POST
def adicionar_ao_carrinho(request, produto_id):
    item = get_object_or_404(Produto, pk=produto_id, ativo=True, vendedor__ativo=True)
    quantidade = _quantidade(request.POST.get("quantidade", "1"))
    if quantidade is None:
        messages.error(request, "Informe uma quantidade entre 1 e 99.")
        return redirect(item)
    atual = ler_carrinho(request)
    nova_quantidade = atual.get(str(item.pk), 0) + quantidade
    if nova_quantidade > item.estoque or nova_quantidade > 99:
        messages.error(request, f"Há apenas {item.estoque} unidade(s) de {item.nome} disponíveis.")
        return redirect(item)
    atual[str(item.pk)] = nova_quantidade
    request.session["carrinho"] = atual
    messages.success(request, f"{item.nome} adicionado ao carrinho.")
    return redirect("loja:carrinho")


@require_POST
def atualizar_carrinho(request, produto_id):
    atual = ler_carrinho(request)
    chave = str(produto_id)
    if chave not in atual:
        return redirect("loja:carrinho")
    try:
        quantidade = int(request.POST.get("quantidade", ""))
    except (TypeError, ValueError):
        quantidade = -1
    if quantidade == 0:
        atual.pop(chave)
    elif 1 <= quantidade <= 99:
        item = get_object_or_404(Produto, pk=produto_id, ativo=True, vendedor__ativo=True)
        if quantidade > item.estoque:
            messages.error(request, f"Há apenas {item.estoque} unidade(s) de {item.nome} disponíveis.")
            return redirect("loja:carrinho")
        atual[chave] = quantidade
    else:
        messages.error(request, "Informe uma quantidade entre 0 e 99.")
        return redirect("loja:carrinho")
    request.session["carrinho"] = atual
    return redirect("loja:carrinho")


def finalizar(request):
    resumo = detalhes_carrinho(request)
    if not resumo["itens"]:
        messages.info(request, "Adicione produtos antes de finalizar seu pedido.")
        return redirect("loja:catalogo")

    aplicar_cupom = request.method == "POST" and request.POST.get("acao") == "aplicar"
    if aplicar_cupom:
        formulario = PedidoForm(initial={campo: request.POST.get(campo, "") for campo in PedidoForm.Meta.fields})
    else:
        formulario = PedidoForm(request.POST or None)
    codigo_cupom = request.POST.get("cupom", "").strip().upper()[:30] if request.method == "POST" else ""
    desconto_preview = ZERO
    if request.method == "POST":
        if aplicar_cupom:
            try:
                cupom = buscar_cupom(codigo_cupom, resumo["subtotais"])
                if cupom:
                    desconto_preview = sum(calcular_descontos(resumo["subtotais"], cupom).values(), ZERO)
                else:
                    formulario.add_error(None, "Digite um código de cupom.")
            except ErroPedido as erro:
                formulario.add_error(None, str(erro))
        elif formulario.is_valid():
            try:
                pedido = criar_pedido(formulario, ler_carrinho(request), codigo_cupom)
            except ErroPedido as erro:
                formulario.add_error(None, str(erro))
            else:
                request.session["carrinho"] = {}
                confirmacoes = request.session.get("pedidos_confirmados", [])
                request.session["pedidos_confirmados"] = [*confirmacoes[-29:], str(pedido.numero)]
                return redirect("loja:pedido_confirmado", numero=pedido.numero)

    return render(request, "loja/finalizar.html", {
        **resumo,
        "form": formulario,
        "codigo_cupom": codigo_cupom,
        "desconto_preview": desconto_preview,
        "total_preview": resumo["subtotal"] - desconto_preview,
    })


@never_cache
def pedido_confirmado(request, numero):
    if str(numero) not in request.session.get("pedidos_confirmados", []):
        raise Http404
    pedido = get_object_or_404(Pedido.objects.prefetch_related("entregas__itens", "entregas__vendedor"), numero=numero)
    resposta = render(request, "loja/pedido_confirmado.html", {"pedido": pedido})
    resposta["Referrer-Policy"] = "no-referrer"
    return resposta
