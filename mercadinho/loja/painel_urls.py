from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import painel_views

app_name = "painel"

urlpatterns = [
    path("", painel_views.dashboard, name="dashboard"),
    path("entrar/", auth_views.LoginView.as_view(
        template_name="loja/painel/login.html", next_page=reverse_lazy("painel:dashboard"),
    ), name="login"),
    path("sair/", auth_views.LogoutView.as_view(next_page=reverse_lazy("loja:inicio")), name="logout"),
    path("relatorio.csv", painel_views.exportar, name="exportar"),
    path("pedidos/", painel_views.pedidos, name="pedidos"),
    path("pedidos/<int:pk>/", painel_views.pedido, name="pedido"),
    path("<str:recurso>/", painel_views.catalogo, name="catalogo"),
    path("<str:recurso>/novo/", painel_views.editar, name="novo"),
    path("<str:recurso>/<int:pk>/editar/", painel_views.editar, name="editar"),
    path("<str:recurso>/<int:pk>/excluir/", painel_views.excluir, name="excluir"),
]
