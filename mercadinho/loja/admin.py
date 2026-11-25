from django.contrib import admin

from .forms import CupomForm, ProdutoForm
from .models import Cupom, ItemPedido, Pedido, Perfil, Produto, Vendedor


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "vendedor", "papel")
    list_filter = ("vendedor", "papel")
    search_fields = ("usuario__username", "vendedor__nome")


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    form = ProdutoForm
    fields = ("vendedor", *ProdutoForm.Meta.fields)
    list_display = ("nome", "vendedor", "categoria", "preco", "estoque", "ativo", "destaque")
    list_filter = ("categoria", "ativo", "destaque", "vendedor")
    search_fields = ("nome", "descricao", "vendedor__nome")
    prepopulated_fields = {"slug": ("nome",)}

    def get_readonly_fields(self, request, obj=None):
        return ("vendedor",) if obj else ()


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    form = CupomForm
    fields = ("vendedor", *CupomForm.Meta.fields)
    list_display = ("codigo", "vendedor", "desconto_percentual", "valido_ate", "ativo")
    list_filter = ("ativo", "vendedor")
    search_fields = ("codigo",)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    can_delete = False
    readonly_fields = ("entrega", "produto", "nome_produto", "quantidade", "preco_unitario", "subtotal")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "nome", "criado_em", "total", "status")
    list_filter = ("status", "criado_em")
    search_fields = ("nome", "email", "numero")
    readonly_fields = (
        "numero", "nome", "email", "telefone", "endereco", "cidade", "cep",
        "cupom", "subtotal", "desconto", "total", "criado_em", "status",
    )
    fields = readonly_fields
    inlines = [ItemPedidoInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
