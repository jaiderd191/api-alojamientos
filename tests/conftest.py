import uuid

import pytest

from app import create_app, db as _db


@pytest.fixture
def app():
    aplicacion = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-key",
            "JWT_EXP_MINUTES": 15,
        }
    )

    with aplicacion.app_context():
        _db.create_all()
        yield aplicacion
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def crear_usuario_y_token(client, prefijo="usuario"):
    correo = f"{prefijo}-{uuid.uuid4().hex[:8]}@ejemplo.com"
    contrasena = "123456"

    client.post(
        "/api/v1/usuarios/registro",
        json={
            "correo": correo,
            "contrasena": contrasena,
        },
    )

    respuesta = client.post(
        "/api/v1/usuarios/login",
        json={
            "correo": correo,
            "contrasena": contrasena,
        },
    )

    token = respuesta.get_json()["data"]["access_token"]

    return correo, {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture
def usuario_auth(client):
    _, headers = crear_usuario_y_token(client)
    return headers


@pytest.fixture
def admin_auth(client):
    from app.dominios.usuarios.repositorios import UsuarioRepositorio

    correo, headers = crear_usuario_y_token(client, "admin")

    with client.application.app_context():
        usuario = UsuarioRepositorio.obtener_por_correo(correo)
        usuario.rol = "admin"
        UsuarioRepositorio.guardar(usuario)

    # El JWT no cambia: identifica al usuario con `sub`.
    # El rol vigente se consulta en la base de datos al autorizar.
    return headers