def test_criar_unidade_sem_token(client):
    resposta = client.post(
        "/unidades", json={"nome": "Matriz", "endereco": "Rua A, 100", "cidade": "Recife"}
    )

    assert resposta.status_code == 401


def test_criar_unidade_perfil_sem_permissao(client, obter_token):
    token = obter_token("cliente@teste.com", "CLIENTE")

    resposta = client.post(
        "/unidades",
        json={"nome": "Matriz", "endereco": "Rua A, 100", "cidade": "Recife"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 403


def test_criar_unidade_admin_sucesso(client, obter_token):
    token = obter_token("admin@teste.com", "ADMIN")

    resposta = client.post(
        "/unidades",
        json={"nome": "Matriz", "endereco": "Rua A, 100", "cidade": "Recife"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Matriz"


def test_criar_unidade_dados_invalidos(client, obter_token):
    token = obter_token("gerente@teste.com", "GERENTE")

    resposta = client.post(
        "/unidades",
        json={"nome": "", "endereco": "Rua A", "cidade": "Recife"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 422


def test_listar_unidades_publico(client, obter_token):
    token = obter_token("admin2@teste.com", "ADMIN")
    client.post(
        "/unidades",
        json={"nome": "Matriz", "endereco": "Rua A, 100", "cidade": "Recife"},
        headers={"Authorization": f"Bearer {token}"},
    )

    resposta = client.get("/unidades")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_obter_unidade_inexistente(client):
    resposta = client.get("/unidades/999")

    assert resposta.status_code == 404