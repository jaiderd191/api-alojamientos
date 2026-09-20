from datetime import UTC, datetime, timedelta

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from app.dominios.usuarios.modelos import PerfilUsuario, Usuario
from app.dominios.usuarios.repositorios import UsuarioRepositorio
from app.errores import ErrorAPI


class UsuarioServicio:
    def __init__(self, secret_key, jwt_exp_minutes=15):
        self.secret_key = secret_key
        self.jwt_exp_minutes = jwt_exp_minutes

    def registrar(self, datos):
        if UsuarioRepositorio.obtener_por_correo(datos["correo"]):
            raise ErrorAPI("El correo ya está registrado.", 409)

        usuario = Usuario(
            correo=datos["correo"],
            contrasena=generate_password_hash(datos["contrasena"]),
        )
        usuario.perfil = PerfilUsuario()
        UsuarioRepositorio.guardar(usuario)
        return usuario

    def login(self, datos):
        usuario = UsuarioRepositorio.obtener_por_correo(datos["correo"])

        if not usuario or not check_password_hash(
            usuario.contrasena,
            datos["contrasena"],
        ):
            raise ErrorAPI("Credenciales inválidas.", 401)

        ahora = datetime.now(UTC)
        token = jwt.encode(
            {
                "sub": str(usuario.id),
                "iat": ahora,
                "exp": ahora + timedelta(minutes=self.jwt_exp_minutes),
            },
            self.secret_key,
            algorithm="HS256",
        )

        return {
            "access_token": token,
            "usuario": usuario.to_dict(),
        }

    def obtener_perfil(self, usuario_id):
        perfil = UsuarioRepositorio.obtener_perfil(usuario_id)

        if not perfil:
            raise ErrorAPI("Perfil no encontrado.", 404)

        return perfil.to_dict()

    def listar_usuarios(self):
        return [
            usuario.to_dict()
            for usuario in UsuarioRepositorio.listar_todos()
        ]

    def promover_admin(self, correo):
        usuario = UsuarioRepositorio.obtener_por_correo(correo)

        if not usuario:
            raise ErrorAPI("Usuario no encontrado.", 404)

        usuario.rol = "admin"
        UsuarioRepositorio.guardar(usuario)
        return usuario