import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.dominios.usuarios.servicios import UsuarioServicio
from app.errores import ErrorAPI


if len(sys.argv) != 2:
    raise SystemExit(
        "Uso: python scripts/promover_admin.py correo@ejemplo.com"
    )

app = create_app()

with app.app_context():
    servicio = UsuarioServicio(
        app.config["SECRET_KEY"],
        app.config["JWT_EXP_MINUTES"],
    )

    try:
        usuario = servicio.promover_admin(sys.argv[1])
    except ErrorAPI as error:
        raise SystemExit(str(error)) from error

    print(f"{usuario.correo} ahora tiene rol admin")