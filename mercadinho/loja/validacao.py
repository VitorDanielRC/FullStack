from django.core.exceptions import ValidationError

from .models import Cupom, Produto


def validar_slug(vendedor_id, slug, produto_id=None):
    duplicados = Produto.objects.filter(vendedor_id=vendedor_id, slug=slug).exclude(pk=produto_id)
    if duplicados.exists():
        raise ValidationError("Este identificador já está em uso nesta loja.")
    return slug


def validar_codigo(codigo, cupom_id=None):
    codigo = codigo.strip().upper()
    if len(codigo) > Cupom._meta.get_field("codigo").max_length:
        raise ValidationError("Use até 30 caracteres no código do cupom.")
    if Cupom.objects.filter(codigo__iexact=codigo).exclude(pk=cupom_id).exists():
        raise ValidationError("Este código não está disponível.")
    return codigo
