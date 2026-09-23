import uuid
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse


class Vendedor(models.Model):
    nome = models.CharField(max_length=120)
    descricao = models.CharField(max_length=240, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "vendedores"

    def __str__(self):
        return self.nome


class Produto(models.Model):
    class Categoria(models.TextChoices):
        DESPENSA = "despensa", "Despensa"
        BEBIDAS = "bebidas", "Bebidas"
        FRESCOS = "frescos", "Frescos"
        CASA = "casa", "Casa"

    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.PROTECT,
        related_name="produtos",
    )
    nome = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    descricao = models.TextField()
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField(default=0)
    imagem_url = models.URLField(blank=True, verbose_name="URL da imagem")
    icone = models.CharField(
        max_length=8,
        default="🛒",
        help_text="Ícone usado quando não há imagem",
    )
    cor = models.CharField(
        max_length=7,
        default="#E7EBD6",
        validators=[
            RegexValidator(
                r"^#[0-9A-Fa-f]{6}$",
                "Use uma cor hexadecimal, como #E7EBD6.",
            )
        ],
        help_text="Cor de fundo em hexadecimal",
    )
    destaque = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "produtos"

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("loja:produto", kwargs={"slug": self.slug})


class Cupom(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    desconto_percentual = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    ativo = models.BooleanField(default=True)
    valido_ate = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["codigo"]
        verbose_name = "cupom"
        verbose_name_plural = "cupons"

    def __str__(self):
        return f"{self.codigo} ({self.desconto_percentual}%)"


class Pedido(models.Model):
    class Status(models.TextChoices):
        RECEBIDO = "recebido", "Recebido"
        PREPARANDO = "preparando", "Preparando"
        ENVIADO = "enviado", "Enviado"
        CONCLUIDO = "concluido", "Concluído"

    numero = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200, verbose_name="Endereço")
    cidade = models.CharField(max_length=100)
    cep = models.CharField(max_length=10, verbose_name="CEP")
    cupom = models.ForeignKey(
        Cupom,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEBIDO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido {str(self.numero)[:8].upper()}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens",
    )
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    nome_produto = models.CharField(max_length=140)
    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "item do pedido"
        verbose_name_plural = "itens do pedido"

    def __str__(self):
        return f"{self.quantidade} × {self.nome_produto}"