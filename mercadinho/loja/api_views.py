from django.db import IntegrityError, transaction
from django.utils.cache import add_never_cache_headers
from django.utils.functional import cached_property
from rest_framework import mixins, permissions, serializers, viewsets
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .acesso import perfil_ativo
from .catalogo import filtrar_produtos
from .dashboard import metricas, pedidos_do_vendedor
from .forms import PeriodoForm
from .models import Cupom, ItemPedido, PedidoVendedor, Produto, Vendedor
from .serializers import (
    CupomSerializer, ItemPedidoSerializer, PedidoVendedorDetalheSerializer,
    PedidoVendedorSerializer, ProdutoSerializer, StatusEntregaSerializer, VendedorSerializer,
)


class PermissaoVendedor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(view.perfil and (
            view.perfil.eh_admin or (not view.admin_exclusivo and (
                request.method in permissions.SAFE_METHODS or view.operador_pode_escrever
            ))
        ))


class AcessoVendedor:
    permission_classes = [permissions.IsAuthenticated, PermissaoVendedor]
    admin_exclusivo = False
    operador_pode_escrever = False

    @cached_property
    def perfil(self):
        return perfil_ativo(self.request.user)

    def finalize_response(self, request, response, *args, **kwargs):
        resposta = super().finalize_response(request, response, *args, **kwargs)
        add_never_cache_headers(resposta)
        return resposta


class RegistroEmUso(APIException):
    status_code = 409
    default_detail = "Este registro está ligado a pedidos e pode apenas ser desativado."


class CatalogoViewSet(AcessoVendedor, viewsets.ModelViewSet):
    def get_queryset(self):
        return self.modelo.objects.filter(vendedor_id=self.perfil.vendedor_id).order_by("pk")

    def _salvar(self, serializer, **campos):
        try:
            with transaction.atomic():
                serializer.save(**campos)
        except IntegrityError as erro:
            raise serializers.ValidationError({"detail": "O identificador já está em uso."}) from erro

    def perform_create(self, serializer):
        self._salvar(serializer, vendedor_id=self.perfil.vendedor_id)

    def perform_update(self, serializer):
        self._salvar(serializer)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_object(self):
        if self.action in ("update", "partial_update"):
            objeto = get_object_or_404(self.get_queryset().select_for_update(), pk=self.kwargs["pk"])
            self.check_object_permissions(self.request, objeto)
            return objeto
        return super().get_object()

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except IntegrityError as erro:
            raise RegistroEmUso from erro


class ProdutoViewSet(CatalogoViewSet):
    modelo = Produto
    serializer_class = ProdutoSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.action == "list":
            queryset, _, _ = filtrar_produtos(queryset, self.request.query_params)
        return queryset


class CupomViewSet(CatalogoViewSet):
    modelo = Cupom
    serializer_class = CupomSerializer
    admin_exclusivo = True


class VendedorViewSet(AcessoVendedor, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = VendedorSerializer

    def get_queryset(self):
        return Vendedor.objects.filter(pk=self.perfil.vendedor_id).order_by("pk")


class PedidoViewSet(AcessoVendedor, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    http_method_names = ["get", "patch", "head", "options"]
    operador_pode_escrever = True

    def get_queryset(self):
        pedidos = PedidoVendedor.objects.filter(vendedor_id=self.perfil.vendedor_id)
        pedidos = pedidos.select_related("pedido").order_by("-pedido__criado_em", "pk")
        return pedidos.prefetch_related("itens") if self.action == "retrieve" else pedidos

    def get_serializer_class(self):
        if self.action == "partial_update":
            return StatusEntregaSerializer
        if self.action == "retrieve":
            return PedidoVendedorDetalheSerializer
        return PedidoVendedorSerializer


class ItemPedidoViewSet(AcessoVendedor, viewsets.ReadOnlyModelViewSet):
    serializer_class = ItemPedidoSerializer

    def get_queryset(self):
        return ItemPedido.objects.filter(entrega__vendedor_id=self.perfil.vendedor_id).order_by("pk")


class DashboardAPI(AcessoVendedor, APIView):
    def get(self, request):
        form = PeriodoForm(request.query_params)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)
        pedidos = pedidos_do_vendedor(self.perfil.vendedor_id, form.cleaned_data)
        dados = metricas(pedidos, self.perfil.eh_admin)
        dados["totais"]["valor"] = format(dados["totais"]["valor"], ".2f")
        return Response(dados)
