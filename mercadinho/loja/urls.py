from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("produtos/", views.catalogo, name="catalogo"),
    path("carrinho/", views.ver_carrinho, name="ver_carrinho"),
    path(
        "carrinho/adicionar/<int:produto_id>/",
        views.adicionar_carrinho,
        name="adicionar_carrinho",
    ),
    path("pedido/finalizar/", views.finalizar_pedido, name="finalizar_pedido"),
]