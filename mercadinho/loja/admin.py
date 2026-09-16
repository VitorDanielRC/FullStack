from django.contrib import admin

from .models import Cupom, ItemPedido, Pedido, Produto, Vendedor


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "vendedor", "categoria", "preco", "estoque", "ativo", "destaque")
    list_filter = ("categoria", "ativo", "destaque", "vendedor")
    search_fields = ("nome", "descricao")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = ("codigo", "desconto_percentual", "valido_ate", "ativo")
    list_filter = ("ativo",)
    search_fields = ("codigo",)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    can_delete = False
    readonly_fields = ("produto", "nome_produto", "quantidade", "preco_unitario", "subtotal")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "nome", "criado_em", "total", "status")
    list_filter = ("status", "criado_em")
    search_fields = ("nome", "email", "numero")
    readonly_fields = (
        "numero", "nome", "email", "telefone", "endereco", "cidade", "cep",
        "cupom", "subtotal", "desconto", "total", "criado_em",
    )
    fields = readonly_fields + ("status",)
    inlines = [ItemPedidoInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
