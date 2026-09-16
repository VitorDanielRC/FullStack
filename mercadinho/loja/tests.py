from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Cupom, ItemPedido, Pedido, Produto, Vendedor


class FluxoCompraTests(TestCase):
    def setUp(self):
        vendedor = Vendedor.objects.create(nome="Vendedor teste")
        self.produto = Produto.objects.create(
            vendedor=vendedor,
            nome="Café teste",
            slug="cafe-teste",
            descricao="Café especial",
            categoria=Produto.Categoria.BEBIDAS,
            preco=Decimal("20.00"),
            estoque=5,
        )
        self.dados_cliente = {
            "nome": "Ana Silva",
            "email": "ana@example.com",
            "telefone": "21999999999",
            "endereco": "Rua das Flores, 10",
            "cidade": "Vassouras",
            "cep": "27700-000",
        }

    def test_pedido_com_cupom_calcula_total_e_baixa_estoque(self):
        Cupom.objects.create(codigo="VILA10", desconto_percentual=10)
        self.client.post(reverse("loja:adicionar", args=[self.produto.pk]), {"quantidade": 2})
        resposta = self.client.post(reverse("loja:finalizar"), {**self.dados_cliente, "cupom": "vila10"})
        pedido = Pedido.objects.get()
        item = ItemPedido.objects.get(pedido=pedido)
        self.produto.refresh_from_db()

        self.assertRedirects(resposta, reverse("loja:pedido_confirmado", args=[pedido.numero]))
        self.assertEqual(pedido.subtotal, Decimal("40.00"))
        self.assertEqual(pedido.desconto, Decimal("4.00"))
        self.assertEqual(pedido.total, Decimal("36.00"))
        self.assertEqual(item.quantidade, 2)
        self.assertEqual(item.preco_unitario, Decimal("20.00"))
        self.assertEqual(self.produto.estoque, 3)
        self.assertEqual(self.client.session["carrinho"], {})

    def test_pedido_com_varios_itens_grava_subtotais(self):
        outro = Produto.objects.create(
            vendedor=self.produto.vendedor,
            nome="Pão teste",
            slug="pao-teste",
            descricao="Pão artesanal",
            categoria=Produto.Categoria.FRESCOS,
            preco=Decimal("7.50"),
            estoque=4,
        )
        self.client.post(reverse("loja:adicionar", args=[self.produto.pk]), {"quantidade": 2})
        self.client.post(reverse("loja:adicionar", args=[outro.pk]), {"quantidade": 3})
        self.client.post(reverse("loja:finalizar"), self.dados_cliente)
        pedido = Pedido.objects.get()
        outro.refresh_from_db()

        self.assertEqual(pedido.itens.count(), 2)
        self.assertEqual(pedido.total, Decimal("62.50"))
        self.assertEqual(outro.estoque, 1)

    def test_estoque_alterado_impede_pedido_sem_baixa_parcial(self):
        self.client.post(reverse("loja:adicionar", args=[self.produto.pk]), {"quantidade": 2})
        self.produto.estoque = 1
        self.produto.save(update_fields=["estoque"])
        resposta = self.client.post(reverse("loja:finalizar"), self.dados_cliente)

        self.assertContains(resposta, "Estoque insuficiente")
        self.assertEqual(Pedido.objects.count(), 0)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, 1)

    def test_cupom_invalido_nao_cria_pedido(self):
        self.client.post(reverse("loja:adicionar", args=[self.produto.pk]), {"quantidade": 1})
        resposta = self.client.post(reverse("loja:finalizar"), {**self.dados_cliente, "cupom": "NAOEXISTE"})

        self.assertContains(resposta, "Cupom inválido ou vencido")
        self.assertEqual(Pedido.objects.count(), 0)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, 5)

    def test_aplicar_cupom_mostra_total_sem_criar_pedido(self):
        Cupom.objects.create(codigo="VILA10", desconto_percentual=10)
        self.client.post(reverse("loja:adicionar", args=[self.produto.pk]), {"quantidade": 1})
        resposta = self.client.post(reverse("loja:finalizar"), {"acao": "aplicar", "cupom": "vila10"})

        self.assertContains(resposta, "Desconto do cupom")
        self.assertNotContains(resposta, "Este campo é obrigatório")
        self.assertEqual(resposta.context["desconto_preview"], Decimal("2.00"))
        self.assertEqual(resposta.context["total_preview"], Decimal("18.00"))
        self.assertEqual(Pedido.objects.count(), 0)

    def test_carrinho_nao_aceita_quantidade_maior_que_estoque(self):
        resposta = self.client.post(reverse("loja:adicionar", args=[self.produto.pk]), {"quantidade": 6})
        self.assertRedirects(resposta, self.produto.get_absolute_url())
        self.assertEqual(self.client.session.get("carrinho", {}), {})

    def test_catalogo_filtra_categoria_e_busca(self):
        resposta = self.client.get(reverse("loja:catalogo"), {"categoria": "bebidas", "q": "Café"})
        self.assertContains(resposta, "Café teste")
        self.assertEqual(list(resposta.context["produtos"]), [self.produto])
