from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .forms import CAMPOS_CUPOM, CAMPOS_PRODUTO
from .models import Cupom, ItemPedido, PedidoVendedor, Produto, Vendedor
from .services import atualizar_status_entrega
from .validacao import validar_codigo, validar_slug


class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = ("id", "nome", "descricao", "ativo")
        read_only_fields = ("ativo",)


class ProdutoSerializer(serializers.ModelSerializer):
    url_publica = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = Produto
        fields = ("id", *CAMPOS_PRODUTO, "url_publica")

    def validate_slug(self, slug):
        try:
            return validar_slug(self.context["view"].perfil.vendedor_id, slug, getattr(self.instance, "pk", None))
        except DjangoValidationError as erro:
            raise serializers.ValidationError(erro.messages) from erro


class CupomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupom
        fields = ("id", *CAMPOS_CUPOM)
        extra_kwargs = {"codigo": {"validators": []}}

    def validate_codigo(self, codigo):
        try:
            return validar_codigo(codigo, getattr(self.instance, "pk", None))
        except DjangoValidationError as erro:
            raise serializers.ValidationError(erro.messages) from erro


class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = ("id", "entrega", "produto", "nome_produto", "quantidade", "preco_unitario", "subtotal")
        read_only_fields = fields


class PedidoVendedorSerializer(serializers.ModelSerializer):
    numero = serializers.UUIDField(source="pedido.numero", read_only=True)
    criado_em = serializers.DateTimeField(source="pedido.criado_em", read_only=True)

    class Meta:
        model = PedidoVendedor
        fields = ("id", "numero", "criado_em", "subtotal", "desconto", "total", "status")
        read_only_fields = fields


class PedidoVendedorDetalheSerializer(PedidoVendedorSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)
    nome = serializers.CharField(source="pedido.nome", read_only=True)
    telefone = serializers.CharField(source="pedido.telefone", read_only=True)
    endereco = serializers.CharField(source="pedido.endereco", read_only=True)
    cidade = serializers.CharField(source="pedido.cidade", read_only=True)
    cep = serializers.CharField(source="pedido.cep", read_only=True)

    class Meta(PedidoVendedorSerializer.Meta):
        fields = (*PedidoVendedorSerializer.Meta.fields, "itens", "nome", "telefone", "endereco", "cidade", "cep")
        read_only_fields = fields


class StatusEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoVendedor
        fields = ("status",)

    def update(self, instance, validated_data):
        if "status" in validated_data:
            atualizar_status_entrega(instance, validated_data["status"])
        return instance
