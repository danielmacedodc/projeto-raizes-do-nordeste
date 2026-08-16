from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health_check() -> dict:
    return {"status": "Running!"}