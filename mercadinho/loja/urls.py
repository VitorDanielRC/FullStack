from django.urls import path

from . import cadastro, views

app_name = "loja"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("produtos/", cadastro.catalogo, name="catalogo"),
    path(
        "produtos/cadastrar/",
        cadastro.cadastrar_produto,
        name="cadastrar_produto",
    ),
    path(
        "produtos/<int:produto_id>/editar/",
        cadastro.editar_produto,
        name="editar_produto",
    ),
    path("carrinho/", views.carrinho, name="carrinho"),
    path(
        "carrinho/adicionar/<int:produto_id>/",
        views.adicionar_ao_carrinho,
        name="adicionar",
    ),
    path(
        "carrinho/atualizar/<int:produto_id>/",
        views.atualizar_carrinho,
        name="atualizar",
    ),
    path("finalizar/", views.finalizar, name="finalizar"),
    path(
        "pedido/<uuid:numero>/",
        views.pedido_confirmado,
        name="pedido_confirmado",
    ),
]