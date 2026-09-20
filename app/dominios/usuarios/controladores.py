from flask import Blueprint, request

from app.dominios.usuarios.dtos import LoginUsuarioDTO, RegistroUsuarioDTO
from app.seguridad import requiere_admin, requiere_token

usuarios_bp = Blueprint("usuarios", __name__)
admin_bp = Blueprint("admin", __name__)
usuario_servicio = None


@usuarios_bp.post("/registro")
def registro():
    datos = RegistroUsuarioDTO().load(
        request.get_json(silent=True) or {}
    )
    usuario = usuario_servicio.registrar(datos)

    return {
        "success": True,
        "data": usuario.to_dict(),
    }, 201


@usuarios_bp.post("/login")
def login():
    datos = LoginUsuarioDTO().load(
        request.get_json(silent=True) or {}
    )

    return {
        "success": True,
        "data": usuario_servicio.login(datos),
    }, 200


@usuarios_bp.get("/perfil")
@requiere_token
def perfil(usuario_id):
    return {
        "success": True,
        "data": usuario_servicio.obtener_perfil(usuario_id),
    }, 200


@admin_bp.get("/usuarios")
@requiere_admin
def listar_usuarios(usuario_id):
    return {
        "success": True,
        "data": usuario_servicio.listar_usuarios(),
    }, 200