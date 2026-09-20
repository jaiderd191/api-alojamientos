from functools import wraps

import jwt
from flask import current_app, request

from app.errores import ErrorAPI


def _usuario_id_desde_token():
    auth_header = request.headers.get("Authorization", "")
    partes = auth_header.split()

    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise ErrorAPI(
            "Se requiere Authorization: Bearer <token>.",
            401,
        )

    try:
        payload = jwt.decode(
            partes[1],
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
        return int(payload["sub"])
    except jwt.ExpiredSignatureError as exc:
        raise ErrorAPI("Token expirado.", 401) from exc
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise ErrorAPI("Token inválido.", 401) from exc


def requiere_token(funcion):
    @wraps(funcion)
    def wrapper(*args, **kwargs):
        usuario_id = _usuario_id_desde_token()
        return funcion(*args, usuario_id=usuario_id, **kwargs)

    return wrapper


def requiere_admin(funcion):
    @wraps(funcion)
    def wrapper(*args, **kwargs):
        from app.dominios.usuarios.repositorios import UsuarioRepositorio

        usuario_id = _usuario_id_desde_token()
        usuario = UsuarioRepositorio.obtener_por_id(usuario_id)

        if not usuario or usuario.rol != "admin":
            raise ErrorAPI("Se requiere rol de administrador.", 403)

        return funcion(*args, usuario_id=usuario_id, **kwargs)

    return wrapper