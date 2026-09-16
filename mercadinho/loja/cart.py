from decimal import Decimal

from .models import Produto


def ler_carrinho(request):
    bruto = request.session.get("carrinho", {})
    if not isinstance(bruto, dict):
        bruto = {}
    carrinho = {}
    for chave, valor in bruto.items():
        try:
            produto_id = int(chave)
            quantidade = int(valor)
        except (TypeError, ValueError):
            continue
        if produto_id > 0 and 0 < quantidade <= 99:
            carrinho[str(produto_id)] = quantidade
    if carrinho != bruto:
        request.session["carrinho"] = carrinho
    return carrinho


def detalhes_carrinho(request):
    carrinho = ler_carrinho(request)
    produtos = Produto.objects.filter(
        pk__in=[int(chave) for chave in carrinho], ativo=True, vendedor__ativo=True
    ).select_related("vendedor")
    itens = []
    subtotal = Decimal("0.00")
    quantidade_total = 0
    encontrados = set()
    for produto in produtos:
        chave = str(produto.pk)
        encontrados.add(chave)
        quantidade = carrinho[chave]
        valor = produto.preco * quantidade
        itens.append({"produto": produto, "quantidade": quantidade, "subtotal": valor})
        subtotal += valor
        quantidade_total += quantidade
    if len(encontrados) != len(carrinho):
        request.session["carrinho"] = {chave: valor for chave, valor in carrinho.items() if chave in encontrados}
    return {"itens": itens, "subtotal": subtotal, "quantidade_total": quantidade_total}


def contagem_carrinho(request):
    return {"contagem_carrinho": sum(ler_carrinho(request).values())}
