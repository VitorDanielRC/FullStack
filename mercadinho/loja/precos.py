from decimal import Decimal, ROUND_HALF_UP


CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")


def calcular_descontos(subtotais, cupom):
    descontos = dict.fromkeys(subtotais, ZERO)
    if not cupom:
        return descontos

    acumulado = ZERO
    desconto_anterior = ZERO
    for vendedor_id, subtotal in sorted(subtotais.items()):
        if cupom.vendedor_id is not None and cupom.vendedor_id != vendedor_id:
            continue
        acumulado += subtotal
        desconto = (acumulado * cupom.desconto_percentual / 100).quantize(CENTAVO, rounding=ROUND_HALF_UP)
        descontos[vendedor_id] = desconto - desconto_anterior
        desconto_anterior = desconto
    return descontos
