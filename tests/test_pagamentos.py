def _criar_pedido(client, token, unidade_id, produto_id, quantidade=1):
    return client.post(
        "/pedidos",
        json={
            "unidade_id": unidade_id,
            "canal": "APP",
            "itens": [{"produto_id": produto_id, "quantidade": quantidade}],
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()


def test_pagamento_aprovado_avanca_status_pedido(client, obter_token, unidade_e_produto):
    token = obter_token("cliente1@teste.com", "CLIENTE")
    pedido = _criar_pedido(
        client, token, unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]
    )

    resposta = client.post(
        "/pagamentos",
        json={"pedido_id": pedido["id"], "metodo": "cartao"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["status"] == "APROVADO"

    pedido_atualizado = client.get(
        f"/pedidos/{pedido['id']}", headers={"Authorization": f"Bearer {token}"}
    ).json()
    assert pedido_atualizado["status"] == "EM_PREPARO"


def test_pagamento_recusado_por_limite_nao_altera_status(client, obter_token):
    token_admin = obter_token("admin1@teste.com", "ADMIN")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    unidade = client.post(
        "/unidades", json={"nome": "Filial", "endereco": "Rua X", "cidade": "Recife"}, headers=headers_admin
    ).json()
    produto = client.post(
        "/produtos", json={"nome": "Combo Premium", "categoria": "Combo", "preco": 600},
        headers=headers_admin,
    ).json()
    client.post(
        "/estoque/movimentacao",
        json={
            "produto_id": produto["id"],
            "unidade_id": unidade["id"],
            "tipo": "ENTRADA",
            "quantidade": 5,
        },
        headers=headers_admin,
    )

    token_cliente = obter_token("cliente2@teste.com", "CLIENTE")
    pedido = _criar_pedido(client, token_cliente, unidade["id"], produto["id"])

    resposta = client.post(
        "/pagamentos",
        json={"pedido_id": pedido["id"], "metodo": "cartao"},
        headers={"Authorization": f"Bearer {token_cliente}"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["status"] == "RECUSADO"

    pedido_atualizado = client.get(
        f"/pedidos/{pedido['id']}", headers={"Authorization": f"Bearer {token_cliente}"}
    ).json()
    assert pedido_atualizado["status"] == "RECEBIDO"


def test_pagamento_duplicado_bloqueado(client, obter_token, unidade_e_produto):
    token = obter_token("cliente3@teste.com", "CLIENTE")
    pedido = _criar_pedido(
        client, token, unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/pagamentos", json={"pedido_id": pedido["id"], "metodo": "cartao"}, headers=headers)
    resposta = client.post(
        "/pagamentos", json={"pedido_id": pedido["id"], "metodo": "pix"}, headers=headers
    )

    assert resposta.status_code == 409


def test_pagamento_pedido_inexistente(client, obter_token):
    token = obter_token("cliente4@teste.com", "CLIENTE")

    resposta = client.post(
        "/pagamentos",
        json={"pedido_id": 999, "metodo": "cartao"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 404


def test_pagamento_sem_token(client, unidade_e_produto):
    resposta = client.post(
        "/pagamentos", json={"pedido_id": 1, "metodo": "cartao"}
    )

    assert resposta.status_code == 401


def test_pagamento_cliente_nao_pode_pagar_pedido_de_outro(client, obter_token, unidade_e_produto):
    token_dono = obter_token("dono@teste.com", "CLIENTE")
    pedido = _criar_pedido(
        client, token_dono, unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]
    )

    token_outro = obter_token("outro@teste.com", "CLIENTE")
    resposta = client.post(
        "/pagamentos",
        json={"pedido_id": pedido["id"], "metodo": "cartao"},
        headers={"Authorization": f"Bearer {token_outro}"},
    )

    assert resposta.status_code == 403


def test_pagamento_modo_aleatorio_aprovado(client, obter_token, unidade_e_produto, monkeypatch):
    from config import settings

    monkeypatch.setattr(settings, "pagamento_mock_modo", "aleatorio")
    monkeypatch.setattr("services.pagamentos.random.random", lambda: 0.1)

    token = obter_token("cliente5@teste.com", "CLIENTE")
    pedido = _criar_pedido(
        client, token, unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]
    )

    resposta = client.post(
        "/pagamentos",
        json={"pedido_id": pedido["id"], "metodo": "cartao"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.json()["status"] == "APROVADO"


def test_pagamento_modo_aleatorio_recusado(client, obter_token, unidade_e_produto, monkeypatch):
    from config import settings

    monkeypatch.setattr(settings, "pagamento_mock_modo", "aleatorio")
    monkeypatch.setattr("services.pagamentos.random.random", lambda: 0.99)

    token = obter_token("cliente6@teste.com", "CLIENTE")
    pedido = _criar_pedido(
        client, token, unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]
    )

    resposta = client.post(
        "/pagamentos",
        json={"pedido_id": pedido["id"], "metodo": "cartao"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.json()["status"] == "RECUSADO"