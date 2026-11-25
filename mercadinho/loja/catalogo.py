from django.db.models import Q

from .models import Produto


def filtrar_produtos(produtos, parametros, *, incluir_vendedor=False):
    busca = parametros.get("q", "").strip()[:100]
    categoria = parametros.get("categoria", "")
    if categoria not in Produto.Categoria.values:
        categoria = ""

    if busca:
        texto = Q(nome__icontains=busca) | Q(descricao__icontains=busca)
        if incluir_vendedor:
            texto |= Q(vendedor__nome__icontains=busca) | Q(vendedor__descricao__icontains=busca)
        produtos = produtos.filter(texto)
    if categoria:
        produtos = produtos.filter(categoria=categoria)

    return produtos, busca, categoria
