from django.urls import path

from . import views

app_name = "loja"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("produtos/", views.catalogo, name="catalogo"),
    path("produtos/<int:vendedor_id>/<slug:slug>/", views.produto, name="produto"),
    path("produtos/<slug:slug>/", views.produto_legado, name="produto_legado"),
    path("carrinho/", views.carrinho, name="carrinho"),
    path("carrinho/adicionar/<int:produto_id>/", views.adicionar_ao_carrinho, name="adicionar"),
    path("carrinho/atualizar/<int:produto_id>/", views.atualizar_carrinho, name="atualizar"),
    path("finalizar/", views.finalizar, name="finalizar"),
    path("pedido/<uuid:numero>/", views.pedido_confirmado, name="pedido_confirmado"),
]
