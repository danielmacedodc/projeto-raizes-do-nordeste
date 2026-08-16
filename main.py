from fastapi import FastAPI

from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raizes do Nordeste - API",
    docs_url="/docs",
)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}