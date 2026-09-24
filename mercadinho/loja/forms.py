from decimal import Decimal

from django import forms

from .models import Pedido, Produto, Vendedor


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["nome_cliente"]
        widgets = {
            "nome_cliente": forms.TextInput(
                attrs={
                    "autocomplete": "name",
                    "placeholder": "Seu nome completo",
                }
            ),
        }


class ProdutoCadastroForm(forms.Form):
    vendedor_nome = forms.CharField(
        label="Nome do vendedor",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Nome do vendedor"}),
    )

    nome = forms.CharField(
        label="Nome do produto",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Ex.: Café em pó"}),
    )

    categoria = forms.ChoiceField(
        label="Categoria",
        choices=Produto.Categoria.choices,
    )

    preco = forms.DecimalField(
        label="Preço",
        max_digits=8,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(
            attrs={"min": "0.01", "step": "0.01", "placeholder": "0,00"}
        ),
    )

    estoque = forms.IntegerField(
        label="Quantidade em estoque",
        min_value=0,
        widget=forms.NumberInput(attrs={"min": "0", "step": "1"}),
    )

    def __init__(self, *args, produto=None, **kwargs):
        self.produto = produto
        super().__init__(*args, **kwargs)

        if produto:
            self.initial["vendedor_nome"] = produto.vendedor.nome
            self.initial["nome"] = produto.nome
            self.initial["categoria"] = produto.categoria
            self.initial["preco"] = produto.preco
            self.initial["estoque"] = produto.estoque

    def save(self):
        nome_vendedor = self.cleaned_data["vendedor_nome"].strip()
        vendedor = Vendedor.objects.filter(nome__iexact=nome_vendedor).first()

        if vendedor is None:
            vendedor = Vendedor.objects.create(
                nome=nome_vendedor,
                ativo=True,
            )
        elif not vendedor.ativo:
            vendedor.ativo = True
            vendedor.save(update_fields=["ativo"])

        produto = self.produto or Produto()
        produto.vendedor = vendedor
        produto.nome = self.cleaned_data["nome"]
        produto.categoria = self.cleaned_data["categoria"]
        produto.preco = self.cleaned_data["preco"]
        produto.estoque = self.cleaned_data["estoque"]
        produto.ativo = True
        produto.save()

        return produto