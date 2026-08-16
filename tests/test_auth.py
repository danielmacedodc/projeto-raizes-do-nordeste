def test_cadastro_usuario_sucesso(client):
    resposta = client.post(
        "/auth/cadastro",
        json={
            "nome": "Maria Silva",
            "email": "maria@teste.com",
            "perfil": "CLIENTE",
            "senha": "senhaforte123",
            "consentimento_lgpd": True,
        },
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == "maria@teste.com"
    assert "senha" not in corpo
    assert "senha_hash" not in corpo


def test_cadastro_email_duplicado(client, registrar_usuario):
    registrar_usuario("duplicado@teste.com", "CLIENTE")

    resposta = client.post(
        "/auth/cadastro",
        json={
            "nome": "Outra Pessoa",
            "email": "duplicado@teste.com",
            "perfil": "CLIENTE",
            "senha": "senhaforte123",
            "consentimento_lgpd": True,
        },
    )

    assert resposta.status_code == 409


def test_login_sucesso(client, registrar_usuario):
    registrar_usuario("login@teste.com", "CLIENTE", senha="senhaforte123")

    resposta = client.post(
        "/auth/login", json={"email": "login@teste.com", "senha": "senhaforte123"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["access_token"]


def test_login_senha_invalida(client, registrar_usuario):
    registrar_usuario("errado@teste.com", "CLIENTE", senha="senhaforte123")

    resposta = client.post(
        "/auth/login", json={"email": "errado@teste.com", "senha": "senhaerrada"}
    )

    assert resposta.status_code == 401


def test_login_email_inexistente(client):
    resposta = client.post(
        "/auth/login", json={"email": "naoexiste@teste.com", "senha": "qualquer123"}
    )

    assert resposta.status_code == 401