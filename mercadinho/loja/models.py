import uuid
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Vendedor(models.Model):
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.PROTECT,
        related_name="produtos",
    )
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    class Categoria(models.TextChoices):
        DESPENSA = "despensa", "Despensa"
        BEBIDAS = "bebidas", "Bebidas"
        FRESCOS = "frescos", "Frescos"
        CASA = "casa", "Casa"

    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.DESPENSA,
    )

class Cupom(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    desconto_percentual = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo


class Pedido(models.Model):
    numero = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    nome_cliente = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)
    cupom = models.ForeignKey(
        Cupom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"Pedido {str(self.numero)[:8]}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens",
    )
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade} × {self.produto.nome}"