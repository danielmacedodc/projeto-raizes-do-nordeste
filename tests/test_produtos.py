def test_criar_produto_sem_token(client):
    resposta = client.post(
        "/produtos", json={"nome": "X-Burger", "categoria": "Lanche", "preco": 19.9}
    )

    assert resposta.status_code == 401


def test_criar_produto_perfil_sem_permissao(client, obter_token):
    token = obter_token("cliente@teste.com", "CLIENTE")

    resposta = client.post(
        "/produtos",
        json={"nome": "X-Burger", "categoria": "Lanche", "preco": 19.9},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 403


def test_criar_produto_admin_sucesso(client, obter_token):
    token = obter_token("admin@teste.com", "ADMIN")

    resposta = client.post(
        "/produtos",
        json={"nome": "X-Burger", "categoria": "Lanche", "preco": 19.9},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["preco"] == "19.90"


def test_criar_produto_preco_invalido(client, obter_token):
    token = obter_token("gerente@teste.com", "GERENTE")

    resposta = client.post(
        "/produtos",
        json={"nome": "X-Burger", "categoria": "Lanche", "preco": -5},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 422


def test_listar_produtos_publico(client, obter_token):
    token = obter_token("admin2@teste.com", "ADMIN")
    client.post(
        "/produtos",
        json={"nome": "X-Burger", "categoria": "Lanche", "preco": 19.9},
        headers={"Authorization": f"Bearer {token}"},
    )

    resposta = client.get("/produtos")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_obter_produto_inexistente(client):
    resposta = client.get("/produtos/999")

    assert resposta.status_code == 404