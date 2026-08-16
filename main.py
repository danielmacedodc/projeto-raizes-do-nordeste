from fastapi import FastAPI

app = FastAPI(
    title="Raizes do Nordeste - API",
    docs_url="/docs",
)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}