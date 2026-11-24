from django import forms

from .models import Cupom, Pedido, Produto
from .validacao import validar_codigo, validar_slug


CAMPOS_PRODUTO = ("nome", "slug", "descricao", "categoria", "preco", "estoque", "imagem_url", "icone", "cor", "destaque", "ativo")
CAMPOS_CUPOM = ("codigo", "desconto_percentual", "ativo", "valido_ate")


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["nome", "email", "telefone", "endereco", "cidade", "cep"]
        widgets = {
            "nome": forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Seu nome completo"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "voce@exemplo.com"}),
            "telefone": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "(21) 99999-9999"}),
            "endereco": forms.TextInput(attrs={"autocomplete": "street-address", "placeholder": "Rua, número e complemento"}),
            "cidade": forms.TextInput(attrs={"autocomplete": "address-level2", "placeholder": "Sua cidade"}),
            "cep": forms.TextInput(attrs={"autocomplete": "postal-code", "placeholder": "00000-000"}),
        }


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = CAMPOS_PRODUTO
        labels = {"slug": "Identificador na URL", "preco": "Preço"}

    def clean_slug(self):
        return validar_slug(self.instance.vendedor_id, self.cleaned_data["slug"], self.instance.pk)


class CupomForm(forms.ModelForm):
    class Meta:
        model = Cupom
        fields = CAMPOS_CUPOM
        labels = {"valido_ate": "Válido até", "desconto_percentual": "Desconto (%)"}
        widgets = {"valido_ate": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})}

    def clean_codigo(self):
        return validar_codigo(self.cleaned_data["codigo"], self.instance.pk)


class PeriodoForm(forms.Form):
    inicio = forms.DateField(label="De", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fim = forms.DateField(label="Até", required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get("inicio"), dados.get("fim")
        if inicio and fim and inicio > fim:
            self.add_error("fim", "A data final deve ser igual ou posterior à data inicial.")
        return dados


class StatusEntregaForm(forms.Form):
    status = forms.ChoiceField(label="Status da entrega", choices=Pedido.Status.choices)
