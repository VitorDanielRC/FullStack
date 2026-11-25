from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .forms import PedidoForm
from .models import Cupom, ItemPedido, Pedido, PedidoVendedor, Perfil, Produto, Vendedor
from .services import criar_pedido


class MarketplaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.loja_a = Vendedor.objects.create(nome="Loja A")
        cls.loja_b = Vendedor.objects.create(nome="Loja B")
        cls.produto_a = Produto.objects.create(
            vendedor=cls.loja_a, nome="Café da Loja A", slug="cafe", descricao="Café da casa",
            categoria=Produto.Categoria.BEBIDAS, preco=Decimal("20.05"), estoque=15,
        )
        cls.produto_b = Produto.objects.create(
            vendedor=cls.loja_b, nome="Café da Loja B", slug="cafe", descricao="Café da casa",
            categoria=Produto.Categoria.BEBIDAS, preco=Decimal("30.05"), estoque=15,
        )
        cls.admin = get_user_model().objects.create_user(username="admin-a")
        cls.operador = get_user_model().objects.create_user(username="operador-a", is_staff=True)
        cls.admin_b = get_user_model().objects.create_user(username="admin-b")
        cls.sem_perfil = get_user_model().objects.create_user(username="cliente")
        Perfil.objects.create(usuario=cls.admin, vendedor=cls.loja_a, papel=Perfil.Papel.ADMIN)
        Perfil.objects.create(usuario=cls.operador, vendedor=cls.loja_a, papel=Perfil.Papel.OPERADOR)
        Perfil.objects.create(usuario=cls.admin_b, vendedor=cls.loja_b, papel=Perfil.Papel.ADMIN)
        cls.cupom = Cupom.objects.create(vendedor=cls.loja_a, codigo="CAFE10", desconto_percentual=10)
        cls.pedido = cls.criar_compra(cls.produto_a, cls.produto_b, codigo="CAFE10")
        cls.entrega_a = cls.pedido.entregas.get(vendedor=cls.loja_a)
        cls.entrega_b = cls.pedido.entregas.get(vendedor=cls.loja_b)
        cls.pedido_b = cls.criar_compra(cls.produto_b)
        instante = timezone.make_aware(datetime(2026, 10, 30, 23, 59))
        Pedido.objects.filter(pk=cls.pedido.pk).update(criado_em=instante)
        outro_dia = timezone.make_aware(datetime(2026, 11, 1, 12, 0))
        Pedido.objects.filter(pk=cls.pedido_b.pk).update(criado_em=outro_dia)

    @staticmethod
    def criar_compra(*produtos, codigo=""):
        form = PedidoForm({
            "nome": "Cliente de teste", "email": "cliente@example.com", "telefone": "24999999999",
            "endereco": "Rua do teste, 123", "cidade": "Vassouras", "cep": "27700-000",
        })
        if not form.is_valid():
            raise ValueError(form.errors)
        return criar_pedido(form, {str(produto.pk): 1 for produto in produtos}, codigo)

    def test_checkout_separa_vendedores_e_aplica_cupom_apenas_no_elegivel(self):
        self.assertEqual(self.entrega_a.total, Decimal("18.04"))
        self.assertEqual(self.entrega_b.total, Decimal("30.05"))
        self.assertEqual(self.pedido.total, Decimal("48.09"))
        self.assertEqual(self.entrega_a.itens.get().produto, self.produto_a)
        self.assertEqual(self.entrega_b.itens.get().produto, self.produto_b)

    def test_resumo_do_cliente_fica_na_sessao_da_compra(self):
        for produto in (self.produto_a, self.produto_b):
            self.client.post(reverse("loja:adicionar", args=[produto.pk]), {"quantidade": 1})
        dados = {
            "nome": "Cliente de teste", "email": "cliente@example.com", "telefone": "24999999999",
            "endereco": "Rua do teste, 123", "cidade": "Vassouras", "cep": "27700-000",
        }
        resposta = self.client.post(reverse("loja:finalizar"), dados, follow=True)
        self.assertContains(resposta, self.produto_a.nome)
        self.assertContains(resposta, self.produto_b.nome)
        url, _ = resposta.redirect_chain[-1]
        vendedor = APIClient()
        vendedor.force_login(self.admin)
        self.assertEqual(vendedor.get(url).status_code, 404)

    def test_cupom_global_rateia_centavos_sem_alterar_total_do_cliente(self):
        Cupom.objects.create(codigo="GLOBAL10", desconto_percentual=10)
        pedido = self.criar_compra(self.produto_a, self.produto_b, codigo="GLOBAL10")
        self.assertEqual(pedido.desconto, Decimal("5.01"))
        self.assertEqual(sum(pedido.entregas.values_list("desconto", flat=True)), pedido.desconto)
        self.assertEqual(sum(pedido.entregas.values_list("total", flat=True)), pedido.total)

    def test_catalogo_publico_exibe_ambas_as_lojas_e_filtra_vendedor(self):
        resposta = self.client.get(reverse("loja:catalogo"), {"vendedor": self.loja_b.pk})
        self.assertContains(resposta, self.produto_b.nome)
        self.assertNotContains(resposta, self.produto_a.nome)
        self.assertContains(self.client.get(self.produto_a.get_absolute_url()), self.produto_a.nome)
        self.assertContains(self.client.get(self.produto_b.get_absolute_url()), self.produto_b.nome)

    def test_busca_categoria_e_paginacao_do_painel_respeitam_o_vendedor(self):
        Produto.objects.bulk_create([
            Produto(
                vendedor=self.loja_a, nome=f"Café especial {i}", slug=f"cafe-especial-{i}",
                descricao="Café torrado", categoria=Produto.Categoria.BEBIDAS, preco=Decimal("25.00"),
            )
            for i in range(25)
        ])
        self.client.force_login(self.admin)
        url = reverse("painel:catalogo", kwargs={"recurso": "produtos"})
        filtro = {"categoria": "bebidas", "q": "CAFé"}
        primeira = self.client.get(url, filtro)
        self.assertContains(primeira, 'value="CAFé"')
        self.assertContains(primeira, "categoria=bebidas&amp;q=CAF%C3%A9&amp;pagina=2")
        self.assertNotContains(primeira, self.produto_b.nome)
        pagina = self.client.get(url, {**filtro, "pagina": 2}).context["pagina"]
        self.assertEqual(pagina.paginator.count, 26)
        self.assertEqual(len(pagina.object_list), 1)
        vazia = self.client.get(url, {**filtro, "categoria": "casa"})
        self.assertContains(vazia, "Nenhum produto encontrado com esses filtros.")

    def test_api_combina_busca_e_categoria_apenas_entre_produtos_do_vendedor(self):
        self.client.force_login(self.admin)
        url = reverse("api:produto-list")
        resposta = self.client.get(url, {"q": "CAFé", "categoria": "bebidas"})
        self.assertEqual([p["id"] for p in resposta.json()["results"]], [self.produto_a.pk])
        self.assertEqual(self.client.get(url, {"q": "café", "categoria": "casa"}).json()["results"], [])

    def test_painel_e_api_exigem_perfil_e_vendedor_ativo(self):
        painel = reverse("painel:dashboard")
        api = reverse("api:produto-list")
        self.assertEqual(self.client.get(painel).status_code, 302)
        self.assertEqual(self.client.get(api).status_code, 403)
        self.client.force_login(self.sem_perfil)
        self.assertEqual(self.client.get(painel).status_code, 403)
        self.assertEqual(self.client.get(api).status_code, 403)
        self.client.force_login(self.admin)
        Vendedor.objects.filter(pk=self.loja_a.pk).update(ativo=False)
        self.assertEqual(self.client.get(painel).status_code, 403)
        self.assertEqual(self.client.get(api).status_code, 403)

    def test_pedido_e_itens_api_e_painel_nao_expoem_a_outra_loja(self):
        self.client.force_login(self.admin)
        resposta = self.client.get(reverse("api:pedido-list"), {"vendedor": self.loja_b.pk}).json()
        self.assertEqual([pedido["id"] for pedido in resposta["results"]], [self.entrega_a.pk])
        detalhe = self.client.get(reverse("api:pedido-detail", args=[self.entrega_a.pk])).json()
        self.assertEqual([item["produto"] for item in detalhe["itens"]], [self.produto_a.pk])
        item_b = self.entrega_b.itens.get()
        self.assertEqual(self.client.get(reverse("api:item-detail", args=[item_b.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("api:pedido-detail", args=[self.entrega_b.pk])).status_code, 404)
        painel_a = self.client.get(reverse("painel:pedido", args=[self.entrega_a.pk]))
        self.assertContains(painel_a, self.produto_a.nome)
        self.assertNotContains(painel_a, self.produto_b.nome)
        self.assertEqual(self.client.get(reverse("painel:pedido", args=[self.entrega_b.pk])).status_code, 404)

    def test_api_grava_produto_no_vendedor_da_sessao_e_confere_unicidade(self):
        cliente = APIClient()
        cliente.force_login(self.admin)
        api = reverse("api:produto-list")
        dados = {"nome": "Mel", "slug": "mel", "descricao": "Mel puro", "categoria": "despensa", "preco": "7.50"}
        resposta = cliente.post(api, {**dados, "vendedor": self.loja_b.pk}, format="json")
        self.assertEqual(resposta.status_code, 201, resposta.data)
        self.assertEqual(Produto.objects.get(pk=resposta.data["id"]).vendedor, self.loja_a)
        self.assertEqual(cliente.post(api, dados, format="json").status_code, 400)
        url_b = reverse("api:produto-detail", args=[self.produto_b.pk])
        self.assertEqual(cliente.patch(url_b, {"preco": "1.00"}, format="json").status_code, 404)
        cliente.force_login(self.admin_b)
        self.assertEqual(cliente.post(api, dados, format="json").status_code, 201)

    def test_operador_pode_atualizar_so_sua_entrega_e_nao_gere_catalogo(self):
        cliente = APIClient()
        cliente.force_login(self.operador)
        produto = reverse("api:produto-detail", args=[self.produto_a.pk])
        self.assertEqual(cliente.get(produto).status_code, 200)
        self.assertEqual(cliente.patch(produto, {"estoque": 40}, format="json").status_code, 403)
        self.assertEqual(cliente.get(reverse("api:cupom-list")).status_code, 403)
        self.assertEqual(cliente.get(reverse("painel:exportar")).status_code, 403)
        self.assertEqual(cliente.get(reverse("admin:index")).status_code, 302)
        dados = {"status": Pedido.Status.ENVIADO, "total": "1.00"}
        url_b = reverse("api:pedido-detail", args=[self.entrega_b.pk])
        url_a = reverse("api:pedido-detail", args=[self.entrega_a.pk])
        self.assertEqual(cliente.patch(url_b, dados, format="json").status_code, 404)
        self.assertEqual(cliente.patch(url_a, dados, format="json").status_code, 200)
        self.entrega_a.refresh_from_db()
        self.pedido.refresh_from_db()
        self.assertEqual(self.entrega_a.status, Pedido.Status.ENVIADO)
        self.assertEqual(self.entrega_a.total, Decimal("18.04"))
        self.assertEqual(self.pedido.status, Pedido.Status.RECEBIDO)

    def test_relatorio_aplica_periodo_e_escopo_inclusive_no_csv(self):
        self.client.force_login(self.admin)
        periodo = {"inicio": "2026-10-30", "fim": "2026-10-30"}
        dashboard = self.client.get(reverse("painel:dashboard"), periodo)
        self.assertContains(dashboard, self.produto_a.nome)
        self.assertNotContains(dashboard, self.produto_b.nome)
        dados = dashboard.context["dados"]
        self.assertEqual(dados["totais"]["pedidos"], 1)
        self.assertEqual(dados["totais"]["valor"], Decimal("18.04"))
        self.assertEqual(dados["serie"], [{"mes": "10/2026", "total": 1}])
        csv = self.client.get(reverse("painel:exportar"), periodo)
        self.assertContains(csv, str(self.pedido.numero))
        self.assertNotContains(csv, str(self.pedido_b.numero))
        self.client.force_login(self.admin_b)
        resposta = self.client.get(reverse("api:dashboard"), periodo)
        self.assertEqual(resposta.json()["totais"]["valor"], "30.05")
        self.assertEqual(self.client.get(reverse("api:dashboard"), {"fim": "ontem"}).status_code, 400)
        self.assertEqual(self.client.get(reverse("painel:exportar"), {"fim": "ontem"}).status_code, 400)

    def test_operador_ve_metricas_parciais_e_periodo_vazio_e_tratado(self):
        self.client.force_login(self.operador)
        resposta = self.client.get(reverse("api:dashboard")).json()
        self.assertEqual(resposta["totais"]["pedidos"], 1)
        self.assertNotIn("serie", resposta)
        painel = self.client.get(reverse("painel:dashboard"), {"fim": "2025-01-01"})
        self.assertContains(painel, "Sem produtos vendidos no período.")
        self.assertNotContains(painel, "Baixar CSV")

    def test_cupom_usado_e_item_de_pedido_nao_podem_ser_excluidos(self):
        cliente = APIClient()
        cliente.force_login(self.admin)
        self.assertEqual(cliente.delete(reverse("api:cupom-detail", args=[self.cupom.pk])).status_code, 409)
        item = ItemPedido.objects.get(entrega=self.entrega_a)
        self.assertEqual(cliente.delete(reverse("api:item-detail", args=[item.pk])).status_code, 405)
