import logging


def test_login_gera_log_de_auditoria(client, registrar_usuario, caplog):
    caplog.set_level(logging.INFO, logger="auditoria")
    registrar_usuario("login-log@teste.com", "CLIENTE")

    client.post(
        "/auth/login", json={"email": "login-log@teste.com", "senha": "senhaforte123"}
    )

    assert "acao=login" in caplog.text


def test_criacao_pedido_gera_log_de_auditoria(client, obter_token, unidade_e_produto, caplog):
    caplog.set_level(logging.INFO, logger="auditoria")
    token = obter_token("cliente@teste.com", "CLIENTE")

    client.post(
        "/pedidos",
        json={
            "unidade_id": unidade_e_produto["unidade_id"],
            "canal": "APP",
            "itens": [{"produto_id": unidade_e_produto["produto_id"], "quantidade": 1}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert "acao=pedido_criado" in caplog.text


def test_cancelamento_pedido_gera_log_de_auditoria(
    client, obter_token, unidade_e_produto, caplog
):
    token_cliente = obter_token("cliente2@teste.com", "CLIENTE")
    pedido = client.post(
        "/pedidos",
        json={
            "unidade_id": unidade_e_produto["unidade_id"],
            "canal": "APP",
            "itens": [{"produto_id": unidade_e_produto["produto_id"], "quantidade": 1}],
        },
        headers={"Authorization": f"Bearer {token_cliente}"},
    ).json()

    caplog.set_level(logging.INFO, logger="auditoria")
    token_staff = obter_token("cozinha@teste.com", "COZINHA")
    client.patch(
        f"/pedidos/{pedido['id']}/status",
        json={"status": "CANCELADO"},
        headers={"Authorization": f"Bearer {token_staff}"},
    )

    assert "acao=pedido_cancelado" in caplog.text