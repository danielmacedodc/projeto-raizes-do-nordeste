import os
from pathlib import Path

# precisa ser definido antes de importar config/database/main, pois a Settings()
# do pydantic-settings é instanciada na primeira importação do módulo config
TEST_DB_PATH = Path(__file__).resolve().parent.parent / "test_raizes.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

import pytest
from fastapi.testclient import TestClient

from database import engine
from main import app
from models import Base


@pytest.fixture(autouse=True)
def _banco_limpo():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registrar_usuario(client):
    def _registrar(email: str, perfil: str, senha: str = "senhaforte123") -> None:
        client.post(
            "/auth/cadastro",
            json={
                "nome": "Usuario Teste",
                "email": email,
                "perfil": perfil,
                "senha": senha,
                "consentimento_lgpd": True,
            },
        )

    return _registrar


@pytest.fixture
def obter_token(client, registrar_usuario):
    def _obter_token(email: str, perfil: str, senha: str = "senhaforte123") -> str:
        registrar_usuario(email, perfil, senha)
        resposta = client.post("/auth/login", json={"email": email, "senha": senha})
        return resposta.json()["access_token"]

    return _obter_token


@pytest.fixture
def unidade_e_produto(client, obter_token):
    token = obter_token("admin.setup@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}

    unidade = client.post(
        "/unidades",
        json={"nome": "Matriz", "endereco": "Rua A, 100", "cidade": "Recife"},
        headers=headers,
    ).json()

    produto = client.post(
        "/produtos",
        json={"nome": "X-Burger", "categoria": "Lanche", "preco": 19.9},
        headers=headers,
    ).json()

    return {"unidade_id": unidade["id"], "produto_id": produto["id"]}