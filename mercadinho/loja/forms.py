from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

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


class ProdutoCadastroForm(forms.ModelForm):
    vendedor_nome = forms.CharField(
        label="Nome do vendedor",
        max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Nome do vendedor"}
        ),
    )

    preco = forms.DecimalField(
        label="Preço",
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"step": "0.01", "placeholder": "0,00"}
        ),
    )

    estoque = forms.IntegerField(
        label="Quantidade em estoque",
        widget=forms.NumberInput(attrs={"step": "1"}),
    )

    class Meta:
        model = Produto
        fields = ["nome", "categoria", "preco", "estoque"]

    def __init__(self, *args, produto=None, **kwargs):
        super().__init__(*args, instance=produto, **kwargs)

        if produto:
            self.initial["vendedor_nome"] = produto.vendedor.nome

    def clean_preco(self):
        preco = self.cleaned_data.get("preco")

        if preco is not None and preco <= Decimal("0"):
            raise ValidationError("O preço deve ser maior que zero.")

        return preco

    def clean_estoque(self):
        estoque = self.cleaned_data.get("estoque")

        if estoque is not None and estoque < 0:
            raise ValidationError(
                "A quantidade em estoque não pode ser negativa."
            )

        return estoque

    def save(self, commit=True):
        produto = super().save(commit=False)
        nome_vendedor = self.cleaned_data.get("vendedor_nome", "").strip()

        vendedor = Vendedor.objects.filter(
            nome__iexact=nome_vendedor
        ).first()

        if vendedor is None:
            vendedor = Vendedor.objects.create(
                nome=nome_vendedor,
                descricao="",
                ativo=True,
            )
        elif not vendedor.ativo:
            vendedor.ativo = True
            vendedor.save(update_fields=["ativo"])

        produto.vendedor = vendedor
        produto.ativo = True

        if commit:
            produto.save()

        return produto