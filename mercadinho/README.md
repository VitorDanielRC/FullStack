# Mercado da Vila · Marketplace P2

Marketplace em Django 6 (Python 3.12+). O cliente pode comprar de vários vendedores no mesmo carrinho. A confirmação grava um pedido para o cliente, uma entrega por vendedor e a baixa de estoque em uma transação. Cada vendedor acompanha somente suas entregas e seus valores.

## Rodar localmente (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Abra a [vitrine](http://127.0.0.1:8000/). O comando `seed_demo` cria oito produtos, três vendedores e o cupom global `VILA10` sem sobrescrever cadastros existentes. Um cupom cadastrado por um vendedor incide somente nos produtos daquela loja.

## Acesso à gestão

1. Crie a conta da plataforma com `.\.venv\Scripts\python.exe manage.py createsuperuser`.
2. Entre no [Django Admin](http://127.0.0.1:8000/admin/) com essa conta. Em **Usuários**, crie as contas dos vendedores sem marcar equipe ou superusuário.
3. Em **Loja → Perfis**, associe cada usuário a um vendedor ativo e a um papel. Use duas contas com vendedores diferentes para demonstrar o isolamento.
4. Entre no [Painel do vendedor](http://127.0.0.1:8000/painel/) com uma das contas criadas.

| Operação | Administrador do vendedor | Operador |
| --- | --- | --- |
| Consultar produtos, pedidos e itens da própria loja | Sim | Sim |
| Atualizar o status de entrega | Sim | Sim |
| Gerenciar produtos e cupons | Sim | — |
| Ver indicadores, ranking e distribuição por status | Sim | Sim |
| Ver a série mensal e exportar CSV | Sim | — |

O dashboard usa a data do pedido no fuso `America/Sao_Paulo`. O valor apresentado é o total dos pedidos registrados, com desconto, e não representa pagamentos recebidos.

## API REST

A [interface do DRF](http://127.0.0.1:8000/api/) usa a mesma sessão Django do painel. As listas são paginadas. Operações de escrita autenticadas por sessão exigem o token CSRF.

| Rota | Operações |
| --- | --- |
| `/api/vendedores/` | Consultar o próprio vendedor. Administradores podem atualizar nome e descrição pelo detalhe. |
| `/api/produtos/` | Consultar, criar, editar e excluir produtos da própria loja conforme o papel. |
| `/api/cupons/` | Administrar cupons da própria loja. |
| `/api/pedidos/` | Consultar entregas e usar `PATCH /api/pedidos/{id}/` para atualizar `status`. |
| `/api/itens/` | Consultar itens das entregas da própria loja. |
| `/api/dashboard/?inicio=AAAA-MM-DD&fim=AAAA-MM-DD` | Consultar as métricas do mesmo período do painel. |

Os pedidos são criados pelo checkout público para manter a validação de estoque, preços e descontos em um único fluxo. Produtos e cupons já usados em pedidos podem ser desativados. O resumo completo da compra fica disponível na sessão do cliente que a concluiu.

## Banco de dados

Por padrão, o projeto usa SQLite para começar sem configurar um servidor. Para PostgreSQL, instale `requirements-postgres.txt` e defina as variáveis `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT` antes de rodar as migrações. As variáveis necessárias para produção estão exemplificadas em `.env.example`. O arquivo `.env` não é carregado automaticamente; exporte as variáveis no ambiente de execução.

Ao atualizar da P1, faça uma cópia do banco antes de `migrate`. Os pedidos e os itens existentes mantêm seus identificadores. A migração atribui cada item ao vendedor atual do produto e rateia o desconto histórico sem alterar o total do pedido. Os cupons antigos continuam globais.

## Testes

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Os testes cobrem o fluxo da P1, a compra com dois vendedores, as permissões por papel, o isolamento entre lojas e o filtro por período no dashboard, na API e no CSV.

## Entrega acadêmica

O arquivo [MELHORIAS_P1.md](MELHORIAS_P1.md) registra a revisão inicial. O backlog está nas issues do repositório:

- [#15 · Marketplace e isolamento](https://github.com/VitorDanielRC/FullStack/issues/15)
- [#16 · Perfis e permissões](https://github.com/VitorDanielRC/FullStack/issues/16)
- [#17 · API REST](https://github.com/VitorDanielRC/FullStack/issues/17)
- [#18 · Dashboard e CSV](https://github.com/VitorDanielRC/FullStack/issues/18)

O pagamento e a entrega continuam combinados com cada vendedor.
