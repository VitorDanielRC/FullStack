# Mercado da Vila — mini e-commerce

MVP em Django 6 (Python 3.12+) com catálogo, busca, filtro por categoria, carrinho na sessão, cupom de desconto e pedido com vários itens. Ao confirmar o pedido, o sistema valida novamente a disponibilidade e baixa o estoque em uma transação. Os cinco modelos pedidos no material da disciplina estão presentes: `Produto`, `Vendedor`, `Pedido`, `ItemPedido` e `Cupom`.

## Rodar localmente (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Abra `http://127.0.0.1:8000/`. O painel para cadastrar vendedores, produtos e cupons fica em `http://127.0.0.1:8000/admin/`. O comando `seed_demo` cria oito produtos, três vendedores e o cupom de exemplo `VILA10`. Pode ser executado novamente sem duplicar registros nem sobrescrever edições.

## Banco de dados

Por padrão, o projeto usa SQLite para começar sem configurar um servidor. Para PostgreSQL, instale `requirements-postgres.txt` e defina as variáveis `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT` antes de rodar as migrações. As variáveis necessárias para produção estão exemplificadas em `.env.example`. O arquivo `.env` não é carregado automaticamente; exporte as variáveis no ambiente de execução.

## Testes

```powershell
.\.venv\Scripts\python.exe manage.py test
```

## Limite do MVP

O site registra pedidos e atualiza o estoque. Não processa pagamentos nem calcula frete; esses detalhes devem ser combinados separadamente. O painel permite atualizar o status do pedido. Marketplace com contas de vendedores, dashboard e API DRF são a evolução P2 descrita no material, ainda fora deste MVP.
