from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Cupom, ItemPedido, Pedido, PedidoVendedor, Produto
from .precos import ZERO, calcular_descontos


class ErroPedido(Exception):
    pass


def buscar_cupom(codigo, vendedor_ids):
    if not codigo:
        return None
    cupom = Cupom.objects.filter(codigo__iexact=codigo.strip(), ativo=True).order_by("pk").first()
    if not cupom or (cupom.valido_ate and cupom.valido_ate < timezone.localdate()):
        raise ErroPedido("Cupom inválido ou vencido.")
    if cupom.vendedor_id is not None and cupom.vendedor_id not in vendedor_ids:
        raise ErroPedido("Este cupom não se aplica aos produtos do carrinho.")
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

    subtotais = {}
    for produto in produtos:
        quantidade = carrinho[str(produto.pk)]
        if not produto.ativo or not produto.vendedor.ativo:
            raise ErroPedido(f"{produto.nome} não está mais disponível.")
        if quantidade > produto.estoque:
            raise ErroPedido(f"Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque}.")
        vendedor_id = produto.vendedor_id
        subtotais[vendedor_id] = subtotais.get(vendedor_id, ZERO) + produto.preco * quantidade

    subtotal = sum(subtotais.values(), ZERO)
    if subtotal >= 100_000_000:
        raise ErroPedido("O valor do carrinho ultrapassa o limite de um pedido.")
    cupom = buscar_cupom(codigo_cupom, subtotais)
    descontos = calcular_descontos(subtotais, cupom)

    pedido = formulario.save(commit=False)
    pedido.cupom = cupom
    pedido.subtotal = subtotal
    pedido.desconto = sum(descontos.values(), ZERO)
    pedido.total = subtotal - pedido.desconto
    pedido.save()

    entregas = {}
    for vendedor_id, subtotal_vendedor in subtotais.items():
        desconto = descontos[vendedor_id]
        entregas[vendedor_id] = PedidoVendedor.objects.create(
            pedido=pedido,
            vendedor_id=vendedor_id,
            subtotal=subtotal_vendedor,
            desconto=desconto,
            total=subtotal_vendedor - desconto,
        )

    for produto in produtos:
        quantidade = carrinho[str(produto.pk)]
        baixados = Produto.objects.filter(pk=produto.pk, estoque__gte=quantidade).update(
            estoque=F("estoque") - quantidade
        )
        if not baixados:
            raise ErroPedido(f"Estoque insuficiente para {produto.nome}.")
        ItemPedido.objects.create(
            pedido=pedido,
            entrega=entregas[produto.vendedor_id],
            produto=produto,
            nome_produto=produto.nome,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=produto.preco * quantidade,
        )
    return pedido


@transaction.atomic
def atualizar_status_entrega(entrega, status):
    # Primeiro bloqueia o pedido para serializar atualizações de vendedores distintos.
    pedido = Pedido.objects.select_for_update().get(pk=entrega.pedido_id)
    entrega.status = status
    entrega.save(update_fields=["status"])
    status_entregas = set(pedido.entregas.values_list("status", flat=True))
    pedido.status = next(etapa for etapa in Pedido.Status.values if etapa in status_entregas)
    pedido.save(update_fields=["status"])
