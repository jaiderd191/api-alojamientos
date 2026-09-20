


import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:
    """Configuración central de la aplicación."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
    JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "15").strip())

    # Base de datos
    _db_user = os.getenv("DB_USER", "root").strip()
    _db_password = os.getenv("DB_PASSWORD", "").strip()
    _db_host = os.getenv("DB_HOST", "localhost").strip()
    _db_port = int(os.getenv("DB_PORT", "3306").strip())
    _db_name = os.getenv("DB_NAME", "alojamientos_db").strip()

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=_db_user,
        password=_db_password,
        host=_db_host,
        port=_db_port,
        database=_db_name,
    ).render_as_string(hide_password=False)

    _cors = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    )
    CORS_ALLOWED_ORIGINS = [
        origen.strip() for origen in _cors.split(",") if origen.strip()
    ]