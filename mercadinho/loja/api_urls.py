from django.urls import path
from rest_framework.routers import DefaultRouter

from . import api_views

app_name = "api"

router = DefaultRouter()
router.register("vendedores", api_views.VendedorViewSet, basename="vendedor")
router.register("produtos", api_views.ProdutoViewSet, basename="produto")
router.register("cupons", api_views.CupomViewSet, basename="cupom")
router.register("pedidos", api_views.PedidoViewSet, basename="pedido")
router.register("itens", api_views.ItemPedidoViewSet, basename="item")

urlpatterns = [path("dashboard/", api_views.DashboardAPI.as_view(), name="dashboard"), *router.urls]
