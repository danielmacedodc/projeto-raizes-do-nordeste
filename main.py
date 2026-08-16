import logging

from fastapi import FastAPI

from database import engine
from models import Base
from routers import router as api_router
from routers.error_handlers import registrar_handlers_de_erro

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

Base.metadata.create_all(bind=engine)

TAGS_METADATA = [
    {"name": "infra", "description": "Health check da aplicação."},
    {"name": "auth", "description": "Cadastro de usuários e emissão de token JWT."},
    {"name": "unidades", "description": "Gestão das unidades da rede (lanchonetes)."},
    {"name": "produtos", "description": "Catálogo de produtos (cardápio)."},
    {"name": "estoque", "description": "Entrada/saída e saldo de estoque por unidade."},
    {
        "name": "pedidos",
        "description": "Criação, consulta e atualização de status de pedidos multicanal "
        "(APP, TOTEM, BALCAO, PICKUP, WEB).",
    },
    {"name": "pagamentos", "description": "Simulação de pagamento via gateway mock."},
    {"name": "fidelidade", "description": "Saldo e resgate de pontos do programa de fidelidade."},
]

app = FastAPI(
    title="Raízes do Nordeste - API",
    description="API para rede de lanchonetes multicanal (App, Totem, Balcão, Pickup, Web).",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
)

registrar_handlers_de_erro(app)
app.include_router(api_router)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}