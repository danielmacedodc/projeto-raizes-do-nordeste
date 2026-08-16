import logging

from fastapi import FastAPI

from database import engine
from models import Base
from routers import router as api_router
from routers.error_handlers import registrar_handlers_de_erro

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raizes do Nordeste - API",
    docs_url="/docs",
)

registrar_handlers_de_erro(app)
app.include_router(api_router)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}