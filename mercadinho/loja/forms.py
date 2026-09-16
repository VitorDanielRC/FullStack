from django import forms

from .models import Pedido


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
