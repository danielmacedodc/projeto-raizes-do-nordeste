def test_erro_404_segue_formato_padrao(client):
    resposta = client.get("/unidades/999")

    assert resposta.status_code == 404
    corpo = resposta.json()
    assert corpo["erro"]["status_code"] == 404
    assert corpo["erro"]["mensagem"] == "Unidade não encontrada"


def test_erro_401_segue_formato_padrao(client):
    resposta = client.post(
        "/unidades", json={"nome": "Matriz", "endereco": "Rua A", "cidade": "Recife"}
    )

    assert resposta.status_code == 401
    corpo = resposta.json()
    assert corpo["erro"]["status_code"] == 401
    assert "erro" in corpo


def test_erro_403_segue_formato_padrao(client, obter_token):
    token = obter_token("cliente@teste.com", "CLIENTE")

    resposta = client.post(
        "/unidades",
        json={"nome": "Matriz", "endereco": "Rua A", "cidade": "Recife"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 403
    assert resposta.json()["erro"]["status_code"] == 403


def test_erro_409_segue_formato_padrao(client, obter_token, unidade_e_produto):
    token = obter_token("cliente2@teste.com", "CLIENTE")
    headers = {"Authorization": f"Bearer {token}"}
    pedido = client.post(
        "/pedidos",
        json={
            "unidade_id": unidade_e_produto["unidade_id"],
            "canal": "APP",
            "itens": [{"produto_id": unidade_e_produto["produto_id"], "quantidade": 1}],
        },
        headers=headers,
    ).json()

    client.post("/pagamentos", json={"pedido_id": pedido["id"], "metodo": "cartao"}, headers=headers)
    resposta = client.post(
        "/pagamentos", json={"pedido_id": pedido["id"], "metodo": "pix"}, headers=headers
    )

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["status_code"] == 409


def test_erro_422_segue_formato_padrao_com_detalhes(client, obter_token):
    token = obter_token("gerente@teste.com", "GERENTE")

    resposta = client.post(
        "/unidades",
        json={"nome": "", "endereco": "Rua A", "cidade": "Recife"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["erro"]["status_code"] == 422
    assert isinstance(corpo["erro"]["detalhes"], list)
    assert len(corpo["erro"]["detalhes"]) >= 1
    assert "campo" in corpo["erro"]["detalhes"][0]
    assert "mensagem" in corpo["erro"]["detalhes"][0]