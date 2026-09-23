from django import forms

from .models import Pedido


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