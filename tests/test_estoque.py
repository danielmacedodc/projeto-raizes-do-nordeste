def _criar_unidade_e_produto(client, headers):
    unidade = client.post(
        "/unidades", json={"nome": "Filial", "endereco": "Rua X", "cidade": "Recife"}, headers=headers
    ).json()
    produto = client.post(
        "/produtos", json={"nome": "Suco", "categoria": "Bebida", "preco": 8.5}, headers=headers
    ).json()
    return unidade, produto


def test_movimentacao_entrada_cria_estoque(client, obter_token):
    token = obter_token("admin1@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    unidade, produto = _criar_unidade_e_produto(client, headers)

    resposta = client.post(
        "/estoque/movimentacao",
        json={
            "produto_id": produto["id"],
            "unidade_id": unidade["id"],
            "tipo": "ENTRADA",
            "quantidade": 50,
        },
        headers=headers,
    )

    assert resposta.status_code == 201
    assert resposta.json()["quantidade"] == 50


def test_movimentacao_entrada_acumula(client, obter_token):
    token = obter_token("admin2@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    unidade, produto = _criar_unidade_e_produto(client, headers)

    payload_base = {"produto_id": produto["id"], "unidade_id": unidade["id"], "tipo": "ENTRADA"}
    client.post("/estoque/movimentacao", json={**payload_base, "quantidade": 30}, headers=headers)
    resposta = client.post(
        "/estoque/movimentacao", json={**payload_base, "quantidade": 20}, headers=headers
    )

    assert resposta.json()["quantidade"] == 50


def test_movimentacao_saida_reduz_saldo(client, obter_token):
    token = obter_token("admin3@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    unidade, produto = _criar_unidade_e_produto(client, headers)

    payload_base = {"produto_id": produto["id"], "unidade_id": unidade["id"]}
    client.post(
        "/estoque/movimentacao", json={**payload_base, "tipo": "ENTRADA", "quantidade": 30}, headers=headers
    )
    resposta = client.post(
        "/estoque/movimentacao", json={**payload_base, "tipo": "SAIDA", "quantidade": 10}, headers=headers
    )

    assert resposta.status_code == 201
    assert resposta.json()["quantidade"] == 20


def test_movimentacao_saida_saldo_insuficiente(client, obter_token):
    token = obter_token("admin4@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    unidade, produto = _criar_unidade_e_produto(client, headers)

    resposta = client.post(
        "/estoque/movimentacao",
        json={
            "produto_id": produto["id"],
            "unidade_id": unidade["id"],
            "tipo": "SAIDA",
            "quantidade": 5,
        },
        headers=headers,
    )

    assert resposta.status_code == 409


def test_movimentacao_produto_inexistente(client, obter_token):
    token = obter_token("admin5@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    unidade, _ = _criar_unidade_e_produto(client, headers)

    resposta = client.post(
        "/estoque/movimentacao",
        json={"produto_id": 999, "unidade_id": unidade["id"], "tipo": "ENTRADA", "quantidade": 10},
        headers=headers,
    )

    assert resposta.status_code == 404


def test_movimentacao_sem_token(client):
    resposta = client.post(
        "/estoque/movimentacao",
        json={"produto_id": 1, "unidade_id": 1, "tipo": "ENTRADA", "quantidade": 10},
    )

    assert resposta.status_code == 401


def test_movimentacao_perfil_sem_permissao(client, obter_token):
    token = obter_token("cliente@teste.com", "CLIENTE")

    resposta = client.post(
        "/estoque/movimentacao",
        json={"produto_id": 1, "unidade_id": 1, "tipo": "ENTRADA", "quantidade": 10},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 403


def test_listar_estoque_sem_token(client):
    resposta = client.get("/estoque")

    assert resposta.status_code == 401


def test_listar_estoque_filtra_por_unidade(client, obter_token):
    token = obter_token("admin6@teste.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}

    unidade_a = client.post(
        "/unidades", json={"nome": "A", "endereco": "Rua A", "cidade": "Recife"}, headers=headers
    ).json()
    unidade_b = client.post(
        "/unidades", json={"nome": "B", "endereco": "Rua B", "cidade": "Recife"}, headers=headers
    ).json()
    produto = client.post(
        "/produtos", json={"nome": "Suco", "categoria": "Bebida", "preco": 8.5}, headers=headers
    ).json()

    client.post(
        "/estoque/movimentacao",
        json={
            "produto_id": produto["id"],
            "unidade_id": unidade_a["id"],
            "tipo": "ENTRADA",
            "quantidade": 10,
        },
        headers=headers,
    )
    client.post(
        "/estoque/movimentacao",
        json={
            "produto_id": produto["id"],
            "unidade_id": unidade_b["id"],
            "tipo": "ENTRADA",
            "quantidade": 40,
        },
        headers=headers,
    )

    resposta = client.get(f"/estoque?unidade_id={unidade_a['id']}", headers=headers)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["items"]) == 1
    assert corpo["items"][0]["quantidade"] == 10


def test_pedido_bloqueado_por_estoque_insuficiente(client, obter_token):
    token_admin = obter_token("admin7@teste.com", "ADMIN")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    unidade, produto = _criar_unidade_e_produto(client, headers_admin)

    client.post(
        "/estoque/movimentacao",
        json={
            "produto_id": produto["id"],
            "unidade_id": unidade["id"],
            "tipo": "ENTRADA",
            "quantidade": 1,
        },
        headers=headers_admin,
    )

    token_cliente = obter_token("clientex@teste.com", "CLIENTE")
    resposta = client.post(
        "/pedidos",
        json={
            "unidade_id": unidade["id"],
            "canal": "APP",
            "itens": [{"produto_id": produto["id"], "quantidade": 2}],
        },
        headers={"Authorization": f"Bearer {token_cliente}"},
    )

    assert resposta.status_code == 409


def test_pedido_sem_estoque_cadastrado_e_bloqueado(client, obter_token):
    token_admin = obter_token("admin8@teste.com", "ADMIN")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    unidade, produto = _criar_unidade_e_produto(client, headers_admin)

    token_cliente = obter_token("clientez@teste.com", "CLIENTE")
    resposta = client.post(
        "/pedidos",
        json={
            "unidade_id": unidade["id"],
            "canal": "APP",
            "itens": [{"produto_id": produto["id"], "quantidade": 1}],
        },
        headers={"Authorization": f"Bearer {token_cliente}"},
    )

    assert resposta.status_code == 409


def test_pedido_sucesso_decrementa_estoque(client, obter_token, unidade_e_produto):
    token = obter_token("clientey@teste.com", "CLIENTE")

    client.post(
        "/pedidos",
        json={
            "unidade_id": unidade_e_produto["unidade_id"],
            "canal": "APP",
            "itens": [{"produto_id": unidade_e_produto["produto_id"], "quantidade": 3}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    token_admin = obter_token("admin.check@teste.com", "ADMIN")
    resposta = client.get(
        f"/estoque?unidade_id={unidade_e_produto['unidade_id']}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )

    saldo = next(
        item
        for item in resposta.json()["items"]
        if item["produto_id"] == unidade_e_produto["produto_id"]
    )
    assert saldo["quantidade"] == 97