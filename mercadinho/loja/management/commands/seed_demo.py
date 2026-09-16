from decimal import Decimal

from django.core.management.base import BaseCommand

from loja.models import Cupom, Produto, Vendedor


class Command(BaseCommand):
    help = "Cadastra vendedores e produtos de demonstração sem alterar registros existentes."

    def handle(self, *args, **options):
        vendedores = {}
        for nome, descricao in [
            ("Sítio Aurora", "Sabores frescos e artesanais."),
            ("Casa Grão", "Alimentos que fazem bem ao dia."),
            ("Quintal Botânico", "Pequenos prazeres naturais."),
        ]:
            vendedores[nome], _ = Vendedor.objects.get_or_create(
                nome=nome, defaults={"descricao": descricao}
            )

        produtos = [
            ("cafe-da-serra", "Café da Serra", "Café especial de torra média, com notas de chocolate e caramelo. Um bom começo para qualquer manhã.", "bebidas", "39.90", 22, "☕", "#DFD2BA", "Casa Grão", True),
            ("pao-artesanal", "Pão artesanal", "Pão de fermentação natural, casca crocante e miolo macio. Feito para dividir à mesa.", "frescos", "18.50", 14, "🥖", "#EBD9B8", "Sítio Aurora", True),
            ("mel-silvestre", "Mel silvestre", "Mel puro de flores silvestres, doce na medida e perfeito para acompanhar frutas e torradas.", "despensa", "27.90", 18, "🍯", "#F4DE9D", "Sítio Aurora", True),
            ("limao-siciliano", "Limão siciliano", "Fresco, perfumado e versátil. Ótimo para receitas, bebidas e aquele toque especial.", "frescos", "12.00", 30, "🍋", "#DFECB6", "Sítio Aurora", True),
            ("azeite-da-casa", "Azeite da casa", "Azeite extravirgem de sabor equilibrado, para finalizar pratos com carinho.", "despensa", "49.90", 16, "🫒", "#DDE8C5", "Casa Grão", False),
            ("cha-de-camomila", "Chá de camomila", "Uma pausa leve e aromática para qualquer hora do dia. Caixa com 20 sachês.", "bebidas", "16.90", 25, "🫖", "#E7E3C5", "Quintal Botânico", False),
            ("granola-crocante", "Granola crocante", "Aveia, castanhas e sementes em uma mistura crocante para deixar o café da manhã melhor.", "despensa", "24.90", 20, "🥣", "#E8D7B8", "Casa Grão", False),
            ("vela-capim-limao", "Vela capim-limão", "Um aroma fresco para dar um clima acolhedor à sua casa. Produção artesanal.", "casa", "32.00", 12, "🕯️", "#E4E8CF", "Quintal Botânico", False),
        ]
        criados = 0
        for slug, nome, descricao, categoria, preco, estoque, icone, cor, vendedor, destaque in produtos:
            _, criado = Produto.objects.get_or_create(
                slug=slug,
                defaults={
                    "nome": nome,
                    "descricao": descricao,
                    "categoria": categoria,
                    "preco": Decimal(preco),
                    "estoque": estoque,
                    "icone": icone,
                    "cor": cor,
                    "vendedor": vendedores[vendedor],
                    "destaque": destaque,
                },
            )
            criados += criado
        Cupom.objects.get_or_create(codigo="VILA10", defaults={"desconto_percentual": 10})
        self.stdout.write(self.style.SUCCESS(f"Demonstração pronta: {criados} produto(s) novo(s). Cupom: VILA10."))
