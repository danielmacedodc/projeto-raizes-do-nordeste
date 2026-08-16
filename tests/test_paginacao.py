def test_paginacao_limita_itens_por_pagina(client, obter_token):
    token = obter_token("admin@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(3):
        client.post(
            "/unidades",
            json={"nome": f"Unidade {i}", "endereco": "Rua A", "cidade": "Recife"},
            headers=headers,
        )

    resposta = client.get("/unidades?page=1&limit=2")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["items"]) == 2
    assert corpo["page"] == 1
    assert corpo["limit"] == 2
    assert corpo["total"] == 3


def test_paginacao_segunda_pagina_traz_o_restante(client, obter_token):
    token = obter_token("admin2@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(3):
        client.post(
            "/unidades",
            json={"nome": f"Unidade {i}", "endereco": "Rua A", "cidade": "Recife"},
            headers=headers,
        )

    resposta = client.get("/unidades?page=2&limit=2")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["items"]) == 1
    assert corpo["page"] == 2
    assert corpo["total"] == 3


def test_paginacao_valores_padrao(client, obter_token):
    token = obter_token("admin3@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/unidades",
        json={"nome": "Matriz", "endereco": "Rua A", "cidade": "Recife"},
        headers=headers,
    )

    resposta = client.get("/unidades")

    corpo = resposta.json()
    assert corpo["page"] == 1
    assert corpo["limit"] == 10


def test_paginacao_page_invalida_422(client):
    resposta = client.get("/unidades?page=0")

    assert resposta.status_code == 422


def test_paginacao_limit_acima_do_maximo_422(client):
    resposta = client.get("/unidades?limit=1000")

    assert resposta.status_code == 422