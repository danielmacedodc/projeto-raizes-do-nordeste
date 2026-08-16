# Raízes do Nordeste — API

API para rede de lanchonetes multicanal (App, Totem, Balcão, Pickup, Web), com pedidos,
estoque por unidade, pagamento mock, programa de fidelidade e autenticação JWT com perfis.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes/dependências)
- Banco de dados: SQLite (arquivo local, sem instalação adicional)

Dependências principais (ver `pyproject.toml`): `fastapi[standard]`, `sqlalchemy`, `pydantic-settings`,
`pwdlib[argon2]` (hash de senha), `pyjwt` (token JWT). Testes: `pytest`.

## Configuração das variáveis de ambiente

Copie o arquivo de exemplo e ajuste os valores:

```
cp .env.example .env
```

Variáveis:

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave usada para assinar o JWT — troque por um valor aleatório próprio | — |
| `ALGORITHM` | Algoritmo de assinatura do JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token de acesso, em minutos | `30` |
| `DATABASE_URL` | URL de conexão do banco (SQLAlchemy, síncrono) | `sqlite:///./raizes.db` |
| `PAGAMENTO_MOCK_MODO` | `deterministico` (aprova até R$ 500) ou `aleatorio` (80% de aprovação) | `deterministico` |

## Instalação das dependências

```
uv sync
```

## Banco de dados

Não há migrations formais (Alembic) neste projeto — as tabelas são criadas automaticamente
via `Base.metadata.create_all()` na subida da aplicação, usando o `DATABASE_URL` configurado.
Não há seed automático; os dados (unidades, produtos, usuários) são criados chamando os
endpoints de cadastro.

## Executar a API

```
uv run uvicorn main:app --reload
```

A API sobe em `http://127.0.0.1:8000`.

## Documentação (Swagger/OpenAPI)

Com a API rodando, acesse:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Rodar os testes

```
uv run pytest -v
```

Os testes usam um banco SQLite isolado (`test_raizes.db`, recriado a cada teste) e não afetam
o banco de desenvolvimento.

## Fluxo principal (ponta a ponta)

1. `POST /auth/cadastro` — cria usuário (perfil `ADMIN`, `GERENTE`, `CLIENTE`, `ATENDENTE` ou `COZINHA`)
2. `POST /auth/login` — retorna o token JWT (`Authorization: Bearer <token>`)
3. `POST /unidades` e `POST /produtos` — cadastro de unidade e produto (ADMIN/GERENTE)
4. `POST /estoque/movimentacao` — entrada de estoque do produto na unidade
5. `POST /pedidos` — cria o pedido (`canalPedido` obrigatório); bloqueia se estoque insuficiente
6. `POST /pagamentos` — processa o pagamento mock; se aprovado, avança o pedido para `EM_PREPARO`
7. `PATCH /pedidos/{id}/status` — staff avança o pedido até `ENTREGUE` (acumula pontos de fidelidade) ou `CANCELADO`
8. `GET /fidelidade/saldo` e `POST /fidelidade/resgate` — consulta e resgate de pontos

## Perfis e permissões

| Perfil | Pode |
|---|---|
| `CLIENTE` | Criar pedido, pagar o próprio pedido, ver os próprios pedidos, fidelidade própria |
| `ATENDENTE`, `COZINHA` | Acima + atualizar status de pedido |
| `GERENTE` | Acima + gerenciar unidades, produtos e estoque |
| `ADMIN` | Todos os recursos |

`GET /unidades` e `GET /produtos` (cardápio) são públicos, sem autenticação.