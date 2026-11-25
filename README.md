# 🛒 Mercado da Vila — Full Stack com Django

Projeto Full Stack desenvolvido com **Python e Django** para simular um mini e-commerce de mercado.

A aplicação possui catálogo de produtos, pesquisa, filtros, carrinho de compras, cupons de desconto, criação de pedidos e controle de estoque.

Na P2, um pedido pode reunir produtos de várias lojas. Cada vendedor acessa seus pedidos, produtos e métricas pelo painel ou pela API REST. Veja [como configurar os acessos da P2](mercadinho/README.md#acesso-à-gestão).

> 🎓 Projeto acadêmico desenvolvido para prática de desenvolvimento web Full Stack.

---

## 🚀 Funcionalidades

* 🏠 Página inicial com produtos em destaque
* 🔎 Pesquisa na vitrine por nome ou descrição de produto e vendedor
* 🗂️ Filtro por categoria e vendedor
* 📦 Página individual de cada produto
* 🛒 Carrinho de compras utilizando sessão do Django
* ➕ Adição, alteração e remoção de produtos do carrinho
* 📊 Validação de estoque
* 🏷️ Sistema de cupons de desconto
* 🧾 Finalização de pedidos
* 🔢 Número único de pedido utilizando UUID
* 📉 Atualização automática do estoque
* ⚙️ Painel administrativo do Django
* Painel do vendedor com papéis de administrador e operador
* API REST, dashboard por loja e exportação CSV
* 🧪 Testes automatizados
* 🗄️ Suporte a SQLite e PostgreSQL

---

## 🛠️ Tecnologias utilizadas

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0.4-092E20?style=for-the-badge\&logo=django\&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge\&logo=html5\&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge\&logo=css3\&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)

---

## 📁 Estrutura do projeto

```text
FullStack/
│
├── README.md
│
└── mercadinho/
    │
    ├── manage.py
    ├── requirements.txt
    ├── requirements-postgres.txt
    ├── .env.example
    │
    ├── mercadinho/
    │   └── Configurações principais do Django
    │
    └── loja/
        ├── models.py
        ├── views.py
        ├── forms.py
        ├── services.py
        ├── cart.py
        ├── urls.py
        ├── tests.py
        ├── templates/
        ├── static/
        ├── management/
        └── migrations/
```

---

## 🧩 Modelos do sistema

Modelos usados pela loja e pelo painel:

| Modelo       | Função                                                         |
| ------------ | -------------------------------------------------------------- |
| `Vendedor`   | Armazena os vendedores responsáveis pelos produtos             |
| `Produto`    | Produtos, preços, estoque, categoria e informações de exibição |
| `Cupom`      | Cupons de desconto com percentual e validade                   |
| `Pedido`     | Dados do cliente, endereço, valores e status                   |
| `ItemPedido` | Produtos e quantidades pertencentes ao pedido                  |
| `PedidoVendedor` | Itens, valores e status da entrega de cada vendedor        |
| `Perfil` | Vincula o usuário a um vendedor e a um papel de acesso               |

---

## 🛍️ Categorias

Atualmente os produtos podem ser cadastrados nas seguintes categorias:

* 🥫 Despensa
* 🥤 Bebidas
* 🥬 Frescos
* 🏠 Casa

---

# 💻 Como executar o projeto

## 1. Clone o repositório

```bash
git clone https://github.com/VitorDanielRC/FullStack.git
```

Entre na pasta:

```bash
cd FullStack/mercadinho
```

---

## 2. Crie um ambiente virtual

### Windows

```powershell
py -m venv .venv
```

Ative:

```powershell
.\.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 4. Execute as migrações

```bash
python manage.py migrate
```

---

## 5. Adicione dados de demonstração

```bash
python manage.py seed_demo
```

O comando cria produtos e vendedores para demonstração.

Também é criado o cupom:

```text
VILA10
```

---

## 6. Crie um administrador

```bash
python manage.py createsuperuser
```

Informe:

* usuário
* e-mail
* senha

---

## 7. Execute o servidor

```bash
python manage.py runserver
```

Depois acesse:

```text
http://127.0.0.1:8000/
```

---

# ⚙️ Painel administrativo

O Django Admin pode ser acessado em:

```text
http://127.0.0.1:8000/admin/
```

O superusuário da plataforma pode administrar:

* Produtos
* Vendedores
* Cupons
* Pedidos
* Estoque
* Perfis dos vendedores

Os vendedores atualizam o status de suas entregas no painel em `http://127.0.0.1:8000/painel/`.

---

# 🛒 Fluxo da aplicação

```text
Cliente
   ↓
Catálogo
   ↓
Produto
   ↓
Carrinho
   ↓
Cupom
   ↓
Finalização
   ↓
Validação do estoque
   ↓
Criação do pedido
   ↓
Atualização do estoque
   ↓
Confirmação
```

---

# 🗄️ Banco de dados

## SQLite

Por padrão, o projeto pode utilizar **SQLite**, facilitando a execução local sem necessidade de instalar um servidor de banco de dados.

---

## PostgreSQL

Também existe suporte para PostgreSQL.

Instale as dependências:

```bash
pip install -r requirements-postgres.txt
```

Configure as variáveis de ambiente:

```env
DJANGO_SECRET_KEY=sua-chave-secreta
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=seu-dominio.com

DB_NAME=mercadinho
DB_USER=postgres
DB_PASSWORD=sua-senha
DB_HOST=localhost
DB_PORT=5432
```

O arquivo:

```text
.env.example
```

contém um exemplo das configurações.

---

# 🧪 Testes

Para executar os testes:

```bash
python manage.py test
```

Os testes verificam partes importantes do funcionamento da aplicação.

---

# 🔐 Regras de negócio

Algumas validações implementadas no projeto incluem:

* Quantidade máxima de produtos no carrinho
* Validação da disponibilidade em estoque
* Produtos inativos não aparecem para compra
* Vendedores inativos não têm produtos exibidos
* Validação de cupons
* Validação novamente do estoque ao criar o pedido
* Atualização de estoque após confirmação
* Registro do preço do produto no momento da compra

---

# 📌 Status do projeto

### P2 implementada

Além do fluxo de compra do MVP, a P2 reúne marketplace, painel de vendedores, dashboard e API REST.

Ainda não possui:

* Pagamento online
* Cálculo automático de frete
* Conta individual para clientes

---

# 🔮 Próximas melhorias

Possíveis evoluções do projeto:

* 👤 Área do cliente
* 📦 Histórico de pedidos do cliente
* 💳 Integração com Mercado Pago
* 🚚 Cálculo de frete
* 🐳 Docker
* ☁️ Deploy em produção
* 📱 Melhorias para dispositivos móveis

---

# 👨‍💻 Autor

### Vitor Daniel

Estudante de **Engenharia de Software**, com interesse em:

* Back-end
* Desenvolvimento Full Stack
* Python
* Django
* APIs
* Banco de dados
* Cibersegurança

GitHub:

[@VitorDanielRC](https://github.com/VitorDanielRC)

---

## ⭐ Projeto

Se gostou do projeto, considere deixar uma ⭐ no repositório.

Isso ajuda a acompanhar a evolução do projeto.

---

<p align="center">
  Desenvolvido com 💻 e Python 🐍
</p>
