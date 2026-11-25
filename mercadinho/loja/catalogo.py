from django.db.models import Q

from .models import Produto


def filtrar_produtos(produtos, parametros):
    busca = parametros.get("q", "").strip()[:100]
    categoria = parametros.get("categoria", "")
    if categoria not in Produto.Categoria.values:
        categoria = ""

    if busca:
        produtos = produtos.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
    if categoria:
        produtos = produtos.filter(categoria=categoria)

    return produtos, busca, categoria
