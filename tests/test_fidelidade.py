def _fluxo_pedido_entregue(client, obter_token, unidade_e_produto, email_cliente="cliente@teste.com"):
    token_cliente = obter_token(email_cliente, "CLIENTE")
    headers_cliente = {"Authorization": f"Bearer {token_cliente}"}

    pedido = client.post(
        "/pedidos",
        json={
            "unidade_id": unidade_e_produto["unidade_id"],
            "canal": "APP",
            "itens": [{"produto_id": unidade_e_produto["produto_id"], "quantidade": 2}],
        },
        headers=headers_cliente,
    ).json()

    client.post(
        "/pagamentos", json={"pedido_id": pedido["id"], "metodo": "cartao"}, headers=headers_cliente
    )

    token_staff = obter_token("cozinha@teste.com", "COZINHA")
    headers_staff = {"Authorization": f"Bearer {token_staff}"}
    client.patch(
        f"/pedidos/{pedido['id']}/status", json={"status": "PRONTO"}, headers=headers_staff
    )
    client.patch(
        f"/pedidos/{pedido['id']}/status", json={"status": "ENTREGUE"}, headers=headers_staff
    )

    return token_cliente


def test_saldo_inicial_zero(client, obter_token):
    token = obter_token("novo@teste.com", "CLIENTE")

    resposta = client.get("/fidelidade/saldo", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    assert resposta.json()["saldo"] == 0


def test_acumulo_pontos_ao_entregar_pedido(client, obter_token, unidade_e_produto):
    token_cliente = _fluxo_pedido_entregue(client, obter_token, unidade_e_produto)

    resposta = client.get(
        "/fidelidade/saldo", headers={"Authorization": f"Bearer {token_cliente}"}
    )

    # valor_total = 19.90 * 2 = 39.80 -> 39 pontos (1 ponto por real, arredondado pra baixo)
    assert resposta.json()["saldo"] == 39


def test_resgate_sucesso_reduz_saldo(client, obter_token, unidade_e_produto):
    token_cliente = _fluxo_pedido_entregue(client, obter_token, unidade_e_produto)
    headers = {"Authorization": f"Bearer {token_cliente}"}

    resposta = client.post("/fidelidade/resgate", json={"pontos": 20}, headers=headers)

    assert resposta.status_code == 201
    assert resposta.json()["tipo"] == "RESGATE"

    saldo = client.get("/fidelidade/saldo", headers=headers).json()["saldo"]
    assert saldo == 19


def test_resgate_saldo_insuficiente(client, obter_token):
    token = obter_token("semsaldo@teste.com", "CLIENTE")

    resposta = client.post(
        "/fidelidade/resgate",
        json={"pontos": 10},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 409


def test_resgate_pontos_invalidos(client, obter_token):
    token = obter_token("invalido@teste.com", "CLIENTE")

    resposta = client.post(
        "/fidelidade/resgate",
        json={"pontos": 0},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 422


def test_saldo_sem_token(client):
    resposta = client.get("/fidelidade/saldo")

    assert resposta.status_code == 401


def test_resgate_sem_token(client):
    resposta = client.post("/fidelidade/resgate", json={"pontos": 10})

    assert resposta.status_code == 401