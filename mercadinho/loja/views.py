from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Cupom, ItemPedido, Pedido, Produto


def inicio(request):
    produtos = Produto.objects.filter(
        ativo=True,
        vendedor__ativo=True,
    ).select_related("vendedor")

    return render(request, "loja/inicio.html", {
        "produtos": produtos,
    })


def catalogo(request):
    produtos = Produto.objects.filter(
        ativo=True,
        vendedor__ativo=True,
    ).select_related("vendedor")

    return render(request, "loja/catalogo.html", {
        "produtos": produtos,
    })


def adicionar_carrinho(request, produto_id):
    produto = get_object_or_404(
        Produto,
        id=produto_id,
        ativo=True,
        vendedor__ativo=True,
    )

    carrinho = request.session.get("carrinho", {})
    chave = str(produto.id)
    quantidade_atual = carrinho.get(chave, 0)

    if quantidade_atual + 1 > produto.estoque:
        messages.error(request, "Não há estoque suficiente.")
    else:
        carrinho[chave] = quantidade_atual + 1
        request.session["carrinho"] = carrinho
        messages.success(request, f"{produto.nome} foi adicionado ao carrinho.")

    return redirect("inicio")


def ver_carrinho(request):
    carrinho = request.session.get("carrinho", {})
    itens = []
    total = Decimal("0.00")

    for produto_id, quantidade in carrinho.items():
        produto = get_object_or_404(Produto, id=produto_id)
        subtotal = produto.preco * quantidade

        itens.append({
            "produto": produto,
            "quantidade": quantidade,
            "subtotal": subtotal,
        })
        total += subtotal

    return render(request, "loja/carrinho.html", {
        "itens": itens,
        "total": total,
    })


@transaction.atomic
def finalizar_pedido(request):
    if request.method != "POST":
        return redirect("ver_carrinho")

    carrinho = request.session.get("carrinho", {})
    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect("ver_carrinho")

    nome_cliente = request.POST.get("nome_cliente", "").strip()
    if not nome_cliente:
        messages.error(request, "Informe seu nome.")
        return redirect("ver_carrinho")

    pedido = Pedido.objects.create(nome_cliente=nome_cliente)
    total = Decimal("0.00")

    for produto_id, quantidade in carrinho.items():
        produto = get_object_or_404(
            Produto.objects.select_for_update(),
            id=produto_id,
            ativo=True,
        )

        if quantidade > produto.estoque:
            messages.error(request, f"Estoque insuficiente para {produto.nome}.")
            return redirect("ver_carrinho")

        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
        )

        total += produto.preco * quantidade
        produto.estoque -= quantidade
        produto.save(update_fields=["estoque"])

    codigo_cupom = request.POST.get("cupom", "").strip().upper()

    if codigo_cupom:
        cupom = Cupom.objects.filter(
            codigo=codigo_cupom,
            ativo=True,
        ).first()

        if cupom:
            pedido.cupom = cupom
            desconto = total * Decimal(cupom.desconto_percentual) / Decimal("100")
            total -= desconto

    pedido.total = max(total, Decimal("0.00"))
    pedido.save()

    request.session["carrinho"] = {}
    messages.success(request, "Pedido realizado com sucesso.")

    return redirect("inicio")