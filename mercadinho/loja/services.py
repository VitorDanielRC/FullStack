from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Cupom, ItemPedido, Produto


class ErroPedido(Exception):
    pass


def buscar_cupom(codigo):
    if not codigo:
        return None
    cupom = Cupom.objects.filter(codigo__iexact=codigo.strip()).first()
    if not cupom or not cupom.ativo or (cupom.valido_ate and cupom.valido_ate < timezone.localdate()):
        raise ErroPedido("Cupom inválido ou vencido.")
    return cupom


@transaction.atomic
def criar_pedido(formulario, carrinho, codigo_cupom=""):
    if not carrinho:
        raise ErroPedido("Seu carrinho está vazio.")

    produtos = list(
        Produto.objects.select_for_update()
        .select_related("vendedor")
        .filter(pk__in=[int(chave) for chave in carrinho])
        .order_by("pk")
    )
    if len(produtos) != len(carrinho):
        raise ErroPedido("Um produto do carrinho não está mais disponível.")

    subtotal = Decimal("0.00")
    for produto in produtos:
        quantidade = carrinho[str(produto.pk)]
        if not produto.ativo or not produto.vendedor.ativo:
            raise ErroPedido(f"{produto.nome} não está mais disponível.")
        if quantidade > produto.estoque:
            raise ErroPedido(f"Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque}.")
        subtotal += produto.preco * quantidade

    cupom = buscar_cupom(codigo_cupom)
    desconto = Decimal("0.00")
    if cupom:
        desconto = (subtotal * cupom.desconto_percentual / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    pedido = formulario.save(commit=False)
    pedido.cupom = cupom
    pedido.subtotal = subtotal
    pedido.desconto = desconto
    pedido.total = subtotal - desconto
    pedido.save()

    for produto in produtos:
        quantidade = carrinho[str(produto.pk)]
        baixados = Produto.objects.filter(pk=produto.pk, estoque__gte=quantidade).update(
            estoque=F("estoque") - quantidade
        )
        if not baixados:
            raise ErroPedido(f"Estoque insuficiente para {produto.nome}.")
        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            nome_produto=produto.nome,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=produto.preco * quantidade,
        )
    return pedido
