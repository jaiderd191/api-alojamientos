def test_registro_exitoso(client):
    respuesta = client.post(
        "/api/v1/usuarios/registro",
        json={
            "correo": "ana@ejemplo.com",
            "contrasena": "123456",
        },
    )
    datos = respuesta.get_json()["data"]

    assert respuesta.status_code == 201
    assert datos["correo"] == "ana@ejemplo.com"
    assert datos["rol"] == "usuario"
    assert "contrasena" not in datos


def test_registro_rechaza_correo_invalido(client):
    respuesta = client.post(
        "/api/v1/usuarios/registro",
        json={
            "correo": "correo-invalido",
            "contrasena": "123456",
        },
    )

    assert respuesta.status_code == 400


def test_registro_correo_duplicado(client):
    datos = {
        "correo": "duplicado@ejemplo.com",
        "contrasena": "123456",
    }

    client.post("/api/v1/usuarios/registro", json=datos)
    respuesta = client.post("/api/v1/usuarios/registro", json=datos)

    assert respuesta.status_code == 409


def test_login_exitoso(client):
    datos = {
        "correo": "login@ejemplo.com",
        "contrasena": "123456",
    }

    client.post("/api/v1/usuarios/registro", json=datos)
    respuesta = client.post("/api/v1/usuarios/login", json=datos)
    cuerpo = respuesta.get_json()["data"]

    assert respuesta.status_code == 200
    assert "access_token" in cuerpo
    assert cuerpo["usuario"]["correo"] == "login@ejemplo.com"


def test_login_incorrecto(client):
    respuesta = client.post(
        "/api/v1/usuarios/login",
        json={
            "correo": "nadie@ejemplo.com",
            "contrasena": "incorrecta",
        },
    )

    assert respuesta.status_code == 401


def test_perfil_sin_token(client):
    respuesta = client.get("/api/v1/usuarios/perfil")

    assert respuesta.status_code == 401


def test_perfil_con_token(client, usuario_auth):
    respuesta = client.get(
        "/api/v1/usuarios/perfil",
        headers=usuario_auth,
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json()["data"]["usuario_id"] is not None


def test_admin_con_usuario_normal(client, usuario_auth):
    respuesta = client.get(
        "/api/v1/admin/usuarios",
        headers=usuario_auth,
    )

    assert respuesta.status_code == 403


def test_admin_con_admin(client, admin_auth):
    respuesta = client.get(
        "/api/v1/admin/usuarios",
        headers=admin_auth,
    )

    assert respuesta.status_code == 200
    assert isinstance(respuesta.get_json()["data"], list)