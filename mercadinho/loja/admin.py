from django.contrib import admin

from .models import Cupom, ItemPedido, Pedido, Produto, Vendedor


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "vendedor", "preco", "estoque", "ativo")
    list_filter = ("ativo", "vendedor")
    search_fields = ("nome", "vendedor__nome")


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = ("codigo", "desconto_percentual", "ativo")
    list_filter = ("ativo",)
    search_fields = ("codigo",)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ("produto", "quantidade", "preco_unitario")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("numero", "nome_cliente", "criado_em", "total")
    search_fields = ("nome_cliente", "numero")
    readonly_fields = ("numero", "nome_cliente", "criado_em", "cupom", "total")
    inlines = (ItemPedidoInline,)