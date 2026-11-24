from datetime import datetime, time

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import ItemPedido, Pedido, PedidoVendedor
from .precos import ZERO


def pedidos_do_vendedor(vendedor_id, periodo):
    pedidos = PedidoVendedor.objects.filter(vendedor_id=vendedor_id)
    if periodo.get("inicio"):
        inicio = timezone.make_aware(datetime.combine(periodo["inicio"], time.min))
        pedidos = pedidos.filter(pedido__criado_em__gte=inicio)
    if periodo.get("fim"):
        fim = timezone.make_aware(datetime.combine(periodo["fim"], time.max))
        pedidos = pedidos.filter(pedido__criado_em__lte=fim)
    return pedidos


def metricas(pedidos, incluir_serie):
    totais = pedidos.aggregate(
        pedidos=Count("pk"),
        valor=Sum("total", default=ZERO),
        concluidos=Count("pk", filter=Q(status=Pedido.Status.CONCLUIDO)),
    )
    ranking = list(
        ItemPedido.objects.filter(entrega__in=pedidos)
        .values("produto_id", "produto__nome")
        .annotate(unidades=Sum("quantidade"))
        .order_by("-unidades", "produto_id")[:5]
    )
    contagem = {linha["status"]: linha["total"] for linha in pedidos.values("status").annotate(total=Count("pk"))}
    distribuicao = [
        {"status": codigo, "rotulo": rotulo, "total": contagem.get(codigo, 0)}
        for codigo, rotulo in Pedido.Status.choices
    ]
    dados = {"totais": totais, "ranking": ranking, "distribuicao": distribuicao}
    if incluir_serie:
        meses = (
            pedidos.annotate(mes=TruncMonth("pedido__criado_em"))
            .values("mes")
            .annotate(total=Count("pk"))
            .order_by("mes")
        )
        dados["serie"] = [{"mes": linha["mes"].strftime("%m/%Y"), "total": linha["total"]} for linha in meses]
    return dados
