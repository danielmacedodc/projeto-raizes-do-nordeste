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
    corpo = resposta.json()
    assert len(corpo["items"]) == 1
    assert corpo["total"] == 1


def test_obter_produto_inexistente(client):
    resposta = client.get("/produtos/999")

    assert resposta.status_code == 404


def _criar_produto(client, token):
    return client.post(
        "/produtos",
        json={"nome": "X-Burger", "categoria": "Lanche", "preco": 19.9},
        headers={"Authorization": f"Bearer {token}"},
    ).json()


def test_atualizar_produto_sucesso(client, obter_token):
    token = obter_token("admin3@teste.com", "ADMIN")
    produto = _criar_produto(client, token)

    resposta = client.patch(
        f"/produtos/{produto['id']}",
        json={"preco": 24.90},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["preco"] == "24.90"
    assert corpo["nome"] == "X-Burger"


def test_atualizar_produto_inexistente(client, obter_token):
    token = obter_token("admin4@teste.com", "ADMIN")

    resposta = client.patch(
        "/produtos/999",
        json={"preco": 10},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 404


def test_atualizar_produto_perfil_sem_permissao(client, obter_token):
    token_admin = obter_token("admin5@teste.com", "ADMIN")
    produto = _criar_produto(client, token_admin)

    token_cliente = obter_token("cliente2@teste.com", "CLIENTE")
    resposta = client.patch(
        f"/produtos/{produto['id']}",
        json={"preco": 10},
        headers={"Authorization": f"Bearer {token_cliente}"},
    )

    assert resposta.status_code == 403


def test_atualizar_produto_sem_token(client, obter_token):
    token_admin = obter_token("admin6@teste.com", "ADMIN")
    produto = _criar_produto(client, token_admin)

    resposta = client.patch(f"/produtos/{produto['id']}", json={"preco": 10})

    assert resposta.status_code == 401


def test_excluir_produto_sucesso(client, obter_token):
    token = obter_token("admin7@teste.com", "ADMIN")
    produto = _criar_produto(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    resposta = client.delete(f"/produtos/{produto['id']}", headers=headers)

    assert resposta.status_code == 204

    produto_atualizado = client.get(f"/produtos/{produto['id']}").json()
    assert produto_atualizado["ativo"] is False


def test_excluir_produto_inexistente(client, obter_token):
    token = obter_token("admin8@teste.com", "ADMIN")

    resposta = client.delete(
        "/produtos/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 404


def test_excluir_produto_perfil_sem_permissao(client, obter_token):
    token_admin = obter_token("admin9@teste.com", "ADMIN")
    produto = _criar_produto(client, token_admin)

    token_cliente = obter_token("cliente3@teste.com", "CLIENTE")
    resposta = client.delete(
        f"/produtos/{produto['id']}", headers={"Authorization": f"Bearer {token_cliente}"}
    )

    assert resposta.status_code == 403


def test_excluir_produto_sem_token(client, obter_token):
    token_admin = obter_token("admin10@teste.com", "ADMIN")
    produto = _criar_produto(client, token_admin)

    resposta = client.delete(f"/produtos/{produto['id']}")

    assert resposta.status_code == 401