from fastapi import FastAPI

from database import engine
from models import Base
from routers import router as api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raizes do Nordeste - API",
    docs_url="/docs",
)

app.include_router(api_router)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}