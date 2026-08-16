def _payload_pedido(unidade_id: int, produto_id: int, canal: str = "APP") -> dict:
    return {
        "unidade_id": unidade_id,
        "canal": canal,
        "itens": [{"produto_id": produto_id, "quantidade": 2}],
    }


def test_criar_pedido_sucesso(client, obter_token, unidade_e_produto):
    token = obter_token("cliente@teste.com", "CLIENTE")

    resposta = client.post(
        "/pedidos",
        json=_payload_pedido(unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "RECEBIDO"
    assert corpo["canal"] == "APP"
    assert corpo["valor_total"] == "39.80"
    assert len(corpo["itens"]) == 1


def test_criar_pedido_sem_canal(client, obter_token, unidade_e_produto):
    token = obter_token("cliente2@teste.com", "CLIENTE")
    payload = _payload_pedido(unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"])
    del payload["canal"]

    resposta = client.post(
        "/pedidos", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 422


def test_criar_pedido_canal_invalido(client, obter_token, unidade_e_produto):
    token = obter_token("cliente3@teste.com", "CLIENTE")
    payload = _payload_pedido(
        unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"], canal="DRIVE_THRU"
    )

    resposta = client.post(
        "/pedidos", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 422


def test_criar_pedido_unidade_inexistente(client, obter_token, unidade_e_produto):
    token = obter_token("cliente4@teste.com", "CLIENTE")
    payload = _payload_pedido(999, unidade_e_produto["produto_id"])

    resposta = client.post(
        "/pedidos", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 404


def test_criar_pedido_produto_inexistente(client, obter_token, unidade_e_produto):
    token = obter_token("cliente5@teste.com", "CLIENTE")
    payload = _payload_pedido(unidade_e_produto["unidade_id"], 999)

    resposta = client.post(
        "/pedidos", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 404


def test_criar_pedido_sem_token(client, unidade_e_produto):
    resposta = client.post(
        "/pedidos",
        json=_payload_pedido(unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]),
    )

    assert resposta.status_code == 401


def test_listar_pedidos_filtra_por_canal(client, obter_token, unidade_e_produto):
    token = obter_token("cliente6@teste.com", "CLIENTE")
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/pedidos",
        json=_payload_pedido(
            unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"], canal="APP"
        ),
        headers=headers,
    )
    client.post(
        "/pedidos",
        json=_payload_pedido(
            unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"], canal="TOTEM"
        ),
        headers=headers,
    )

    resposta = client.get("/pedidos?canalPedido=TOTEM", headers=headers)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["items"]) == 1
    assert corpo["items"][0]["canal"] == "TOTEM"


def test_cliente_ve_apenas_seus_pedidos(client, obter_token, unidade_e_produto):
    token_a = obter_token("clienteA@teste.com", "CLIENTE")
    token_b = obter_token("clienteB@teste.com", "CLIENTE")

    client.post(
        "/pedidos",
        json=_payload_pedido(unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]),
        headers={"Authorization": f"Bearer {token_a}"},
    )

    resposta = client.get("/pedidos", headers={"Authorization": f"Bearer {token_b}"})

    assert resposta.status_code == 200
    assert resposta.json()["items"] == []


def test_atualizar_status_transicao_valida(client, obter_token, unidade_e_produto):
    token_cliente = obter_token("cliente7@teste.com", "CLIENTE")
    pedido = client.post(
        "/pedidos",
        json=_payload_pedido(unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]),
        headers={"Authorization": f"Bearer {token_cliente}"},
    ).json()

    token_cozinha = obter_token("cozinha@teste.com", "COZINHA")
    resposta = client.patch(
        f"/pedidos/{pedido['id']}/status",
        json={"status": "EM_PREPARO"},
        headers={"Authorization": f"Bearer {token_cozinha}"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "EM_PREPARO"


def test_atualizar_status_transicao_invalida(client, obter_token, unidade_e_produto):
    token_cliente = obter_token("cliente8@teste.com", "CLIENTE")
    pedido = client.post(
        "/pedidos",
        json=_payload_pedido(unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]),
        headers={"Authorization": f"Bearer {token_cliente}"},
    ).json()

    token_cozinha = obter_token("cozinha2@teste.com", "COZINHA")
    resposta = client.patch(
        f"/pedidos/{pedido['id']}/status",
        json={"status": "ENTREGUE"},
        headers={"Authorization": f"Bearer {token_cozinha}"},
    )

    assert resposta.status_code == 409


def test_atualizar_status_sem_permissao(client, obter_token, unidade_e_produto):
    token_cliente = obter_token("cliente9@teste.com", "CLIENTE")
    pedido = client.post(
        "/pedidos",
        json=_payload_pedido(unidade_e_produto["unidade_id"], unidade_e_produto["produto_id"]),
        headers={"Authorization": f"Bearer {token_cliente}"},
    ).json()

    resposta = client.patch(
        f"/pedidos/{pedido['id']}/status",
        json={"status": "EM_PREPARO"},
        headers={"Authorization": f"Bearer {token_cliente}"},
    )

    assert resposta.status_code == 403


def test_atualizar_status_pedido_inexistente(client, obter_token):
    token_cozinha = obter_token("cozinha3@teste.com", "COZINHA")

    resposta = client.patch(
        "/pedidos/999/status",
        json={"status": "EM_PREPARO"},
        headers={"Authorization": f"Bearer {token_cozinha}"},
    )

    assert resposta.status_code == 404