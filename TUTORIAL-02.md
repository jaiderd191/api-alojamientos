# Tutorial práctico — Sprint 2

## Autenticación y autorización

Este tutorial parte del repositorio **después de haber terminado, revisado e integrado el Sprint 1 en `main`**. No cree un proyecto nuevo y no copie la carpeta `solucion-referencia` sobre su repositorio.

Antes de comenzar lea `SPRINT-02.md`. Allí están los conceptos, criterios de aceptación, alcance y Definition of Done. Aquí se construye la solución paso a paso.

El orden de trabajo será:

```text
regresión Sprint 1
      ↓
Issue + branch
      ↓
configuración Sprint 2
      ↓
tests de registro → implementación
      ↓
migración MySQL
      ↓
tests de login → implementación
      ↓
tests de autenticación → implementación
      ↓
tests de autorización → implementación
      ↓
pytest completo
      ↓
Postman
      ↓
commit + push + PR
```

---

## 0. Requisitos antes de iniciar

Debe disponer de:

- Sprint 1 integrado en `main`;
- Python y el entorno `.venv` creado en Sprint 1;
- MySQL iniciado;
- `alojamientos_db` creada;
- `.env` local configurado;
- Git remoto apuntando a `https://github.com/oflodororni/api-alojamientos.git`;
- Postman instalado.

Si alguno de estos puntos no se cumple, corrija primero el Sprint 1.

---

## 1. Abrir el proyecto y activar el entorno virtual

Abra una terminal y entre a la carpeta del repositorio. Sustituya la ruta de ejemplo por la ruta real de su equipo.

### Windows PowerShell

```powershell
cd C:\ruta\api-alojamientos
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```bat
cd C:\ruta\api-alojamientos
.venv\Scripts\activate.bat
```

### Linux/macOS

```bash
cd /ruta/api-alojamientos
source .venv/Scripts/activate
```

Compruebe:

```bash
python --version
git status
git remote -v
```

El remoto debe mostrar el repositorio de práctica.

---

## 2. Actualizar `main` y comprobar regresión

Ejecute:

```bash
git checkout main
git pull origin main
pytest -q
```

Antes de tocar Sprint 2 debe obtener:

```text
3 passed
```

Esos tres tests pertenecen al Sprint 1. Si fallan, no continúe: Sprint 2 debe construirse sobre una base estable.

Compruebe también que `.env` no esté versionado:

```bash
git ls-files .env
```

No debe imprimir ninguna ruta.

---

## 3. Crear la Issue del Sprint 2

En GitHub abra el repositorio y seleccione **Issues → New issue**.

Título:

```text
Sprint 2: implementar autenticación y autorización
```

Puede usar esta descripción:

```text
## Objetivo
Agregar usuarios, registro, login con JWT y autorización por roles.

## Alcance
- Usuario y PerfilUsuario 1:1
- DTOs
- Repository
- Service
- Controller
- hash de contraseñas
- login con JWT
- Bearer Token
- roles usuario/admin
- migración 001
- pytest
- Postman

## Criterios principales
- registro válido → 201
- correo inválido → 400
- correo duplicado → 409
- login válido → 200 + access_token
- login inválido → 401
- perfil sin token → 401
- perfil con token → 200
- usuario normal en admin → 403
- admin en admin → 200
```

Guarde la Issue.

---

## 4. Crear la rama de trabajo

Desde `main` actualizado:

```bash
git checkout -b feat/sprint-02-autenticacion-autorizacion
```

Compruebe:

```bash
git branch
git status
```

La rama activa debe aparecer con `*`.

---

## 5. Agregar las dependencias del Sprint 2

Abra `requirements.txt` y **reemplace todo su contenido** por:
```
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-CORS==6.0.2
Flask-Migrate==4.1.0
PyMySQL==1.1.2
python-dotenv==1.2.2
pytest==9.0.3
PyJWT==2.10.1
marshmallow==3.23.2
Werkzeug==3.1.8
```

Instale o actualice las dependencias:

```bash
python -m pip install -r requirements.txt
```

Compruebe las nuevas bibliotecas:

```bash
python -c "import jwt, marshmallow, werkzeug; print('dependencias Sprint 2 OK')"
```

Debe obtener:

```text
dependencias Sprint 2 OK
```

En este sprint:

- `PyJWT` firma y valida JWT;
- `marshmallow` valida JSON de entrada;
- `Werkzeug` genera y comprueba hashes de contraseña.

---

## 6. Generar una clave secreta local

No invente una clave corta como `123456`. Genere una cadena aleatoria:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie el resultado. Se utilizará únicamente en su archivo `.env`.

---

## 7. Actualizar `.env.example`

Abra `.env.example` y **reemplace todo el archivo** por:
```env
# Seguridad
SECRET_KEY=reemplaza-por-una-clave-segura-generada-localmente
JWT_EXP_MINUTES=15

# MySQL
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=alojamientos_db

# CORS: orígenes permitidos separados por coma
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

`.env.example` sí se versiona porque documenta las variables necesarias, pero no contiene el secreto real.

---

## 8. Actualizar el `.env` local

Abra `.env`. **No borre sus credenciales MySQL del Sprint 1.** Agregue al principio:

```env
SECRET_KEY=PEGUE_AQUI_LA_CLAVE_GENERADA
JWT_EXP_MINUTES=15
```

Sustituya `PEGUE_AQUI_LA_CLAVE_GENERADA` por el valor generado en el paso anterior.

Ejemplo de estructura, sin revelar sus datos reales:

```env
SECRET_KEY=valor-largo-generado-localmente
JWT_EXP_MINUTES=15
DB_USER=root
DB_PASSWORD=su_clave_local
DB_HOST=localhost
DB_PORT=3306
DB_NAME=alojamientos_db
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

Verifique otra vez:

```bash
git ls-files .env
```

Debe seguir sin mostrar nada.

---

## 9. Actualizar `app/config.py`

Abra `app/config.py` y **reemplace todo el contenido** por:
```python
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
```

Observe que se conservó `URL.create()` del Sprint 1 y solo se agregaron las variables de seguridad.

---

## 10. Permitir configuración específica para tests

En Sprint 1 `create_app()` siempre usaba la configuración normal. Para que pytest pueda utilizar una base aislada, primero haremos que App Factory acepte sobrescrituras de configuración.

Abra `app/__init__.py` y **reemplace temporalmente todo el contenido** por:
```python
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

API_VERSION = "v1"

db = SQLAlchemy()
migrate = Migrate()


def create_app(configuracion=None):
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if configuracion:
        app.config.update(configuracion)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config["CORS_ALLOWED_ORIGINS"])

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "service": "alojamientos-api",
            "version": API_VERSION,
        }, 200

    return app
```

La diferencia importante es:

```python
def create_app(configuracion=None):
    ...
    if configuracion:
        app.config.update(configuracion)
```

Esto permite que los tests cambien la URI de MySQL por SQLite **antes** de inicializar SQLAlchemy.

---

## 11. Preparar pytest con una base aislada

Abra `tests/conftest.py` y **reemplace todo el archivo** por:
```python
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
```

Ahora los tests utilizarán:

```text
sqlite:///:memory:
```

Ejecute los tests heredados:

```bash
pytest -q
```

Debe seguir obteniendo:

```text
3 passed
```

Esto confirma que la preparación de Sprint 2 no rompió Health ni CORS.

---

## 12. Crear la estructura del dominio `usuarios`

Debe quedar:

```text
app/
└── dominios/
    ├── __init__.py
    └── usuarios/
        ├── __init__.py
        ├── modelos.py
        ├── dtos.py
        ├── repositorios.py
        ├── servicios.py
        └── controladores.py
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force app\dominios\usuarios
New-Item -ItemType File -Force app\dominios\__init__.py
New-Item -ItemType File -Force app\dominios\usuarios\__init__.py
New-Item -ItemType File -Force app\dominios\usuarios\modelos.py
New-Item -ItemType File -Force app\dominios\usuarios\dtos.py
New-Item -ItemType File -Force app\dominios\usuarios\repositorios.py
New-Item -ItemType File -Force app\dominios\usuarios\servicios.py
New-Item -ItemType File -Force app\dominios\usuarios\controladores.py
New-Item -ItemType File -Force app\errores.py
New-Item -ItemType File -Force app\seguridad.py
```

### Linux/macOS

```bash
mkdir -p app/dominios/usuarios
touch app/dominios/__init__.py
touch app/dominios/usuarios/__init__.py
touch app/dominios/usuarios/modelos.py
touch app/dominios/usuarios/dtos.py
touch app/dominios/usuarios/repositorios.py
touch app/dominios/usuarios/servicios.py
touch app/dominios/usuarios/controladores.py
touch app/errores.py
touch app/seguridad.py
```

Los dos `__init__.py` pueden permanecer vacíos.

---

# PARTE A — REGISTRO

## 13. Escribir primero los tests de registro

Cree `tests/test_usuarios.py` con **exactamente** este contenido inicial:
```python
def test_registro_exitoso(client):
    respuesta = client.post(
        "/api/v1/usuarios/registro",
        json={
            "correo": "ana@ejemplo.com",
            "contrasena": "123456",
        },
    )

    assert respuesta.status_code == 201


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
```

Ejecute únicamente estos tests:

```bash
pytest tests/test_usuarios.py -q
```

En este momento deben fallar porque `/api/v1/usuarios/registro` todavía no existe. Es normal observar `404`.

El fallo confirma que el test realmente detecta la ausencia de la funcionalidad.

---

## 14. Crear el manejo de errores de aplicación

Abra `app/errores.py` y pegue:
```python
class ErrorAPI(Exception):
    """Error controlado que se transforma en una respuesta HTTP."""

    def __init__(self, mensaje, status_code=400):
        super().__init__(mensaje)
        self.status_code = status_code
```

`ErrorAPI` representa errores esperados de negocio. Posteriormente la App Factory los convertirá en respuestas JSON.

---

## 15. Crear los modelos Usuario y PerfilUsuario

Abra `app/dominios/usuarios/modelos.py` y pegue:
```python
from datetime import datetime

from app import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    rol = db.Column(db.String(20), nullable=False, server_default="usuario")

    perfil = db.relationship(
        "PerfilUsuario",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "correo": self.correo,
            "rol": self.rol,
        }


class PerfilUsuario(db.Model):
    __tablename__ = "perfiles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    apellido = db.Column(db.String(50))
    telefono = db.Column(db.String(20))
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        unique=True,
    )

    usuario = db.relationship("Usuario", back_populates="perfil")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "telefono": self.telefono,
            "usuario_id": self.usuario_id,
        }
```

Observe la relación:

```text
Usuario.perfil          uselist=False
Perfil.usuario_id       ForeignKey + unique=True
```

Esto representa:

```text
Usuario 1 ───── 1 PerfilUsuario
```

`to_dict()` excluye deliberadamente `contrasena`.

---

## 16. Crear los DTOs

Abra `app/dominios/usuarios/dtos.py` y pegue:
```python
from marshmallow import Schema, fields, validate


class RegistroUsuarioDTO(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=6),
    )


class LoginUsuarioDTO(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(required=True, load_only=True)
```

Aunque `LoginUsuarioDTO` se utilizará unas secciones más adelante, lo dejamos creado porque ambos DTO pertenecen al mismo archivo y su código es pequeño.

---

## 17. Crear el Repository

Abra `app/dominios/usuarios/repositorios.py` y pegue:
```python
from app import db
from app.dominios.usuarios.modelos import PerfilUsuario, Usuario


class UsuarioRepositorio:
    @staticmethod
    def guardar(usuario):
        db.session.add(usuario)
        db.session.commit()
        return usuario

    @staticmethod
    def obtener_por_correo(correo):
        return db.session.query(Usuario).filter_by(correo=correo).first()

    @staticmethod
    def obtener_por_id(usuario_id):
        return db.session.get(Usuario, usuario_id)

    @staticmethod
    def obtener_perfil(usuario_id):
        return (
            db.session.query(PerfilUsuario)
            .filter_by(usuario_id=usuario_id)
            .first()
        )

    @staticmethod
    def listar_todos():
        return db.session.query(Usuario).all()
```

En este archivo se concentra el acceso a persistencia. El Controller no hará consultas a SQLAlchemy directamente.

---

## 18. Implementar el Service solo para registro

Abra `app/dominios/usuarios/servicios.py` y pegue esta **primera versión completa**:
```python
from werkzeug.security import generate_password_hash

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
```

Observe dos reglas importantes:

1. un correo repetido produce `409 Conflict`;
2. la contraseña se transforma con `generate_password_hash()` antes de persistirse.

También se crea un `PerfilUsuario` vacío y se asocia a `usuario.perfil`. El `cascade` permite guardar ambos objetos mediante la misma operación del Repository.

---

## 19. Implementar el Controller de registro

Abra `app/dominios/usuarios/controladores.py` y pegue esta **primera versión completa**:
```python
from flask import Blueprint, request

from app.dominios.usuarios.dtos import RegistroUsuarioDTO

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
```

El Controller se ocupa de HTTP:

```text
request JSON
   ↓
RegistroUsuarioDTO
   ↓
Service
   ↓
respuesta + 201
```

---

## 20. Registrar el dominio y los manejadores globales

Ahora sustituya `app/__init__.py` por esta versión completa:
```python
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError

from app.config import Config
from app.errores import ErrorAPI

API_VERSION = "v1"

db = SQLAlchemy()
migrate = Migrate()


def create_app(configuracion=None):
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if configuracion:
        app.config.update(configuracion)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config["CORS_ALLOWED_ORIGINS"])

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "service": "alojamientos-api",
            "version": API_VERSION,
        }, 200

    # Importar los modelos permite que Alembic detecte sus tablas.
    from app.dominios.usuarios import modelos  # noqa: F401
    from app.dominios.usuarios import controladores as usuarios_ctrl
    from app.dominios.usuarios.controladores import admin_bp, usuarios_bp
    from app.dominios.usuarios.servicios import UsuarioServicio

    usuarios_ctrl.usuario_servicio = UsuarioServicio(
        app.config["SECRET_KEY"],
        app.config["JWT_EXP_MINUTES"],
    )

    app.register_blueprint(
        usuarios_bp,
        url_prefix=f"/api/{API_VERSION}/usuarios",
    )
    app.register_blueprint(
        admin_bp,
        url_prefix=f"/api/{API_VERSION}/admin",
    )

    @app.errorhandler(ValidationError)
    def manejar_error_validacion(error):
        return {
            "success": False,
            "error": {
                "message": "Datos inválidos.",
                "details": error.messages,
            },
        }, 400

    @app.errorhandler(ErrorAPI)
    def manejar_error_api(error):
        return {
            "success": False,
            "error": {"message": str(error)},
        }, error.status_code
6
    return app
```

Aunque `admin_bp` todavía no contiene rutas, puede registrarse desde ahora. Esto evita reescribir App Factory en cada etapa del tutorial.

Dos handlers nuevos centralizan errores:

```text
ValidationError → 400
ErrorAPI        → status definido por la regla
```

---

## 21. Generar la migración 001

Sprint 1 ya creó la carpeta `migrations/`. No ejecute nuevamente `flask db init`.

Primero compruebe la conexión real con MySQL:

```bash
python -m scripts.verificar_mysql
```

Después genere la migración con un ID determinístico para que todos los estudiantes tengan el mismo identificador lógico:

```bash
flask --app app.py db migrate -m "crear usuarios y perfiles" --rev-id 001
```

```text
flask: ejecuta la CLI de Flask.
--app app.py: indica que la aplicación está en app.py.
db: utiliza los comandos de Flask-Migrate/Alembic.
migrate: compara los modelos actuales con la base de datos y genera una migración.
-m "crear usuarios y perfiles": agrega una descripción a la migración.
--rev-id 001: asigna el identificador 001 a la revisión.
```

Debe aparecer un archivo parecido a:

```text
migrations/versions/001_crear_usuarios_y_perfiles.py
```

Abra el archivo generado y revise que incluya la creación de `usuarios` y `perfiles`. No ejecute `upgrade` sin revisar la migración.

Aplique la migración:

```bash
flask --app app.py db upgrade
```

Compruebe la revisión actual:

```bash
flask --app app.py db current
```

También puede verificar que los modelos y las migraciones estén sincronizados:

```bash
flask --app app.py db check
```

Si no existen cambios pendientes, la comprobación debe finalizar correctamente.

### Verificar desde MySQL

Si utiliza la consola MySQL:

```sql
USE alojamientos_db;
SHOW TABLES;
DESCRIBE usuarios;
DESCRIBE perfiles;
SELECT * FROM alembic_version;
```

Si la herramienta `mysql` no está disponible en su terminal, ejecute las mismas consultas en MySQL Workbench u otro cliente SQL.

Debe observar las tablas `usuarios`, `perfiles` y `alembic_version`.

---

## 22. Ejecutar los tests de registro

```bash
pytest tests/test_usuarios.py -q
```

Esperado:

```text
3 passed
```

Ejecute además toda la regresión:

```bash
pytest -q
```

Esperado en este punto:

```text
6 passed
```

---

# PARTE B — LOGIN Y JWT

## 23. Ampliar primero los tests para login

Reemplace **todo** `tests/test_usuarios.py` por:
```python
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
```

Ejecute:

```bash
pytest tests/test_usuarios.py -q
```

Los tres casos de registro deben seguir pasando y los dos casos de login deben fallar porque `/login` todavía no existe.

---

## 24. Ampliar el Service con login y JWT

Reemplace **todo** `app/dominios/usuarios/servicios.py` por:
```python
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
```

En `login()` sucede:

```text
buscar usuario por correo
        ↓
check_password_hash()
        ↓
crear claims sub/iat/exp
        ↓
jwt.encode(..., HS256)
        ↓
access_token
```

---

## 25. Ampliar el Controller con `/login`

Reemplace **todo** `app/dominios/usuarios/controladores.py` por:
```python
from flask import Blueprint, request

from app.dominios.usuarios.dtos import LoginUsuarioDTO, RegistroUsuarioDTO

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
```

Ejecute:

```bash
pytest -q
```

Esperado:

```text
8 passed
```

---

# PARTE C — AUTENTICACIÓN CON BEARER TOKEN

## 26. Preparar fixtures de usuarios autenticados

Ahora los tests necesitan crear usuarios y reutilizar JWT. Reemplace **todo** `tests/conftest.py` por la versión final:
```python
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
```

Los fixtures preparan datos; no sustituyen las reglas de la aplicación.

`usuario_auth` retorna un diccionario como:

```python
{
    "Authorization": "Bearer eyJ..."
}
```

`admin_auth` crea un usuario, obtiene su JWT y modifica su rol directamente como preparación del escenario de prueba. El mismo token continúa identificando al mismo usuario.

Ejecute para asegurarse de no haber roto los tests existentes:

```bash
pytest -q
```

Debe continuar mostrando `8 passed`.

---

## 27. Escribir los tests del perfil protegido

Reemplace **todo** `tests/test_usuarios.py` por:
```python
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
```

Ejecute:

```bash
pytest tests/test_usuarios.py -q
```

Los dos tests de perfil deben fallar porque el endpoint todavía no está implementado.

---

## 28. Crear `@requiere_token`

Abra `app/seguridad.py` y pegue esta primera versión completa:
```python
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
```

Este código exige exactamente el esquema:

```http
Authorization: Bearer <token>
```

Si falta, expira o no puede validarse, se produce `401`.

---

## 29. Agregar `obtener_perfil()` al Service

Reemplace **todo** `app/dominios/usuarios/servicios.py` por:
```python
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
```

---

## 30. Agregar `GET /perfil` al Controller

Reemplace **todo** `app/dominios/usuarios/controladores.py` por:
```python
from flask import Blueprint, request

from app.dominios.usuarios.dtos import LoginUsuarioDTO, RegistroUsuarioDTO
from app.seguridad import requiere_token

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
```

Observe el orden de decoradores:

```python
@usuarios_bp.get("/perfil")
@requiere_token
def perfil(usuario_id):
    ...
```

El decorador de seguridad obtiene `usuario_id` del JWT y lo entrega al Controller.

Ejecute:

```bash
pytest -q
```

Esperado:

```text
10 passed
```

---

# PARTE D — AUTORIZACIÓN POR ROL

## 31. Escribir primero los tests administrativos

Reemplace **todo** `tests/test_usuarios.py` por su versión final:
```python
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
```

Ejecute:

```bash
pytest tests/test_usuarios.py -q
```

Los casos anteriores deben seguir pasando. Los dos tests administrativos deben fallar porque `/api/v1/admin/usuarios` todavía no tiene una ruta implementada.

---

## 32. Completar `app/seguridad.py` con `@requiere_admin`

Reemplace **todo** el archivo por:
```python
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
```

`@requiere_admin` reutiliza la validación del JWT y después consulta el rol **actual** del usuario en la base de datos.

---

## 33. Completar el Service con administración

Reemplace **todo** `app/dominios/usuarios/servicios.py` por la versión final:
```python
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
```

Ahora existen:

```text
listar_usuarios()
promover_admin(correo)
```

`promover_admin()` se usará mediante un script de consola para preparar el usuario administrador de la práctica.

---

## 34. Completar el Controller administrativo

Reemplace **todo** `app/dominios/usuarios/controladores.py` por la versión final:
```python
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
```

El nuevo endpoint es:

```http
GET /api/v1/admin/usuarios
```

porque App Factory ya registró `admin_bp` con `/api/v1/admin`.

---

## 35. Crear el script para promover un usuario

El directorio `scripts/` ya existe desde Sprint 1. Cree `scripts/promover_admin.py`.

### Windows PowerShell

```powershell
New-Item -ItemType File -Force scripts\promover_admin.py
```

### Linux/macOS

```bash
touch scripts/promover_admin.py
```

Pegue:
```python
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
```

---

## 36. Ejecutar toda la suite automatizada

Ejecute:

```bash
pytest -q
```

El resultado final del Sprint 2 debe ser:

```text
12 passed
```

Si un test del Sprint 1 falla, el Sprint 2 tampoco está terminado.

Opcionalmente puede observar nombres individuales:

```bash
pytest -v
```

---

## 37. Comprobar que la contraseña quedó hasheada en MySQL

Primero iniciaremos la API y registraremos datos manuales en Postman en las siguientes secciones. Después puede ejecutar en MySQL:

```sql
SELECT id, correo, contrasena, rol
FROM usuarios;
```

La columna `contrasena` **no debe contener `123456` literalmente**. Debe contener un hash largo generado por Werkzeug.

No publique ese valor aunque sea un hash.

---

# PARTE E — PRUEBA MANUAL EN POSTMAN

## 38. Iniciar la API

En una terminal con `.venv` activo:

```bash
flask --app app.py run --debug
```

Debe quedar disponible en:

```text
http://localhost:5000
```

Mantenga esta terminal abierta. Use otra terminal para comandos como `promover_admin.py`.

---

## 39. Crear o actualizar el Environment de Postman

En Postman cree un Environment llamado:

```text
Alojamientos API - Sprint 02
```

Agregue estas variables:

| Variable | Valor inicial durante la práctica |
|---|---|
| `baseUrl` | `http://localhost:5000` |
| `token_usuario` | vacío |
| `token_admin` | vacío |

Los tokens se completarán después del login.

Seleccione este Environment antes de enviar peticiones.

---

## 40. Crear la colección

Cree una colección llamada:

```text
Alojamientos API - Sprint 02
```

Cree estas carpetas dentro de ella:

```text
00 - Health
01 - Registro
02 - Login
03 - Autenticación
04 - Autorización
```

---

## 41. Verificar regresión de Health en Postman

En `00 - Health` cree:

```http
GET {{baseUrl}}/health
```

Opcionalmente agregue el header del Sprint 1:

```text
Origin: http://localhost:5173
```

Envíe. Debe responder `200`.

---

## 42. Registrar un usuario normal

En `01 - Registro` cree:

```http
POST {{baseUrl}}/api/v1/usuarios/registro
```

Seleccione **Body → raw → JSON** y escriba:

```json
{
  "correo": "usuario@ejemplo.com",
  "contrasena": "123456"
}
```

Esperado:

```text
201 Created
```

Compruebe que la respuesta no contiene `contrasena`.

---

## 43. Probar validación 400

Duplique la petición anterior y cambie el body a:

```json
{
  "correo": "correo-invalido",
  "contrasena": "123456"
}
```

Esperado:

```text
400 Bad Request
```

Observe `error.details`: esa información proviene de Marshmallow.

---

## 44. Probar conflicto 409

Vuelva a enviar exactamente el registro de:

```text
usuario@ejemplo.com
```

Esperado:

```text
409 Conflict
```

---

## 45. Iniciar sesión como usuario

En `02 - Login` cree:

```http
POST {{baseUrl}}/api/v1/usuarios/login
```

Body:

```json
{
  "correo": "usuario@ejemplo.com",
  "contrasena": "123456"
}
```

Esperado:

```text
200 OK
```

Busque:

```text
data.access_token
```

Copie el token y asígnelo como valor de la variable Postman:

```text
token_usuario
```

No agregue la palabra `Bearer` dentro de la variable; Postman la agregará mediante el tipo de autorización.

---

## 46. Probar login incorrecto

Duplique Login y cambie la contraseña:

```json
{
  "correo": "usuario@ejemplo.com",
  "contrasena": "incorrecta"
}
```

Esperado:

```text
401 Unauthorized
```

---

## 47. Probar `/perfil` sin token

En `03 - Autenticación` cree:

```http
GET {{baseUrl}}/api/v1/usuarios/perfil
```

No configure Authorization todavía.

Esperado:

```text
401 Unauthorized
```

---

## 48. Probar `/perfil` con Bearer Token

Duplique la petición anterior. En **Authorization** seleccione:

```text
Type: Bearer Token
Token: {{token_usuario}}
```

Envíe.

Esperado:

```text
200 OK
```

Ahora Postman envía conceptualmente:

```http
Authorization: Bearer eyJ...
```

---

## 49. Probar el endpoint admin con usuario normal

En `04 - Autorización` cree:

```http
GET {{baseUrl}}/api/v1/admin/usuarios
```

Authorization:

```text
Bearer Token → {{token_usuario}}
```

Esperado:

```text
403 Forbidden
```

El usuario está autenticado, pero no está autorizado.

---

## 50. Registrar el candidato a administrador

Cree otro registro:

```json
{
  "correo": "admin@ejemplo.com",
  "contrasena": "123456"
}
```

Debe responder `201`. Inicialmente su rol también es `usuario`.

---

## 51. Obtener el token del candidato admin ANTES de promoverlo

Haga login con:

```json
{
  "correo": "admin@ejemplo.com",
  "contrasena": "123456"
}
```

Copie `data.access_token` en:

```text
token_admin
```

Con ese token llame:

```http
GET {{baseUrl}}/api/v1/admin/usuarios
Authorization: Bearer {{token_admin}}
```

Esperado antes de promover:

```text
403 Forbidden
```

---

## 52. Promover al usuario desde consola

Abra una **segunda terminal**, entre al proyecto y active `.venv`.

Ejecute:

```bash
python scripts/promover_admin.py admin@ejemplo.com
```

Esperado:

```text
admin@ejemplo.com ahora tiene rol admin
```

No vuelva a iniciar sesión todavía. Queremos comprobar una característica del diseño.

---

## 53. Reutilizar el MISMO JWT después de la promoción

Vuelva a enviar en Postman:

```http
GET {{baseUrl}}/api/v1/admin/usuarios
Authorization: Bearer {{token_admin}}
```

Ahora debe responder:

```text
200 OK
```

¿Por qué funciona el mismo token?

```text
JWT.sub identifica al usuario
        ↓
requiere_admin consulta MySQL
        ↓
el rol actual ahora es admin
```

El rol no se almacenó dentro del JWT.

---

## 54. Exportar Postman como evidencia versionada

Antes de exportar, **borre los valores reales** de:

```text
token_usuario
token_admin
```

No comparta JWT reales en GitHub.

Exporte la colección y el environment en formato JSON.

Guárdelos dentro de:

```text
docs/postman/
```

Con nombres sugeridos:

```text
Alojamientos-API-Sprint-02.postman_collection.json
Alojamientos-API-Sprint-02.postman_environment.json
```

Los archivos exportados por Postman pueden contener identificadores o metadatos diferentes a los de la solución de referencia. Lo importante es que las peticiones, variables y URLs sean equivalentes y que no contengan secretos.

---

# PARTE F — CIERRE DEL SPRINT

## 55. Revisión técnica antes de Git

Ejecute:

```bash
pytest -q
python scripts/verificar_mysql.py
flask --app app.py db current
git status
```

Debe tener:

```text
12 passed
```

Revise además:

```bash
git ls-files .env
```

No debe mostrar `.env`.

Busque accidentalmente secretos antes del commit. No deben existir tokens reales ni la `SECRET_KEY` local en archivos versionados.

---

## 56. Revisar la estructura resultante

El repositorio debe parecerse a:

```text
api-alojamientos/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── errores.py
│   ├── seguridad.py
│   └── dominios/
│       ├── __init__.py
│       └── usuarios/
│           ├── __init__.py
│           ├── modelos.py
│           ├── dtos.py
│           ├── repositorios.py
│           ├── servicios.py
│           └── controladores.py
├── migrations/
│   └── versions/
│       └── 001_...py
├── scripts/
│   ├── verificar_mysql.py
│   └── promover_admin.py
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   └── test_usuarios.py
├── docs/postman/
├── .env.example
├── .gitignore
├── app.py
├── pytest.ini
└── requirements.txt
```

El nombre exacto del archivo de migración puede contener diferencias en el texto descriptivo, pero su `revision` debe ser `001` si utilizó `--rev-id 001`.

---

## 57. Ver cambios antes de hacer commit

```bash
git status
git diff
```

Si todo es correcto:

```bash
git add .
git status
```

Revise cuidadosamente lo que quedó en staging.

---

## 58. Crear el commit del sprint

```bash
git commit -m "feat: completar autenticacion y autorizacion"
```

---

## 59. Hacer push a GitHub

```bash
git push -u origin feat/sprint-02-autenticacion-autorizacion
```

El push es obligatorio: el Sprint no termina con código existente únicamente en el equipo local.

---

## 60. Crear el Pull Request

En GitHub cree un Pull Request:

```text
base: main
compare: feat/sprint-02-autenticacion-autorizacion
```

Título sugerido:

```text
Sprint 2: autenticación y autorización
```

Descripción sugerida:

```text
## Qué se implementó
- dominio usuarios por capas
- Usuario 1:1 PerfilUsuario
- registro y validación
- hash de contraseñas
- login con JWT
- Bearer Token
- roles usuario/admin
- migración 001
- tests automatizados
- colección Postman Sprint 2

## Pruebas
- pytest: 12 passed
- Postman: registro 201
- Postman: duplicado 409
- Postman: login 200
- Postman: perfil sin token 401
- Postman: perfil con token 200
- Postman: usuario en admin 403
- Postman: admin en admin 200

## Seguridad
- .env no versionado
- tokens Postman eliminados antes de exportar
```

Relacione la Issue si corresponde.

---

## 61. Review y merge

Antes de hacer merge compruebe nuevamente la Definition of Done de `SPRINT-02.md`.

Después de la revisión, integre el PR a `main` según el flujo definido por el docente.

Actualice su copia local:

```bash
git checkout main
git pull origin main
```

Ejecute una última vez:

```bash
pytest -q
```

Debe continuar mostrando:

```text
12 passed
```

Ese `main` será el punto de partida exacto del Sprint 3.

---

## 62. Sprint Review

Demuestre al grupo o docente:

1. `pytest -q` en verde;
2. tablas `usuarios` y `perfiles`;
3. registro;
4. login;
5. Bearer Token;
6. diferencia práctica entre `401` y `403`;
7. promoción a admin;
8. acceso administrativo;
9. Pull Request integrado.

---

## 63. Retrospectiva

Registre brevemente:

```text
¿Qué salió bien?
¿Qué parte fue más difícil?
¿Qué diferencia quedó clara entre autenticación y autorización?
¿Qué mejoraríamos para el Sprint 3?
```

---

# Checkpoint final de archivos

Si necesita comparar su resultado, estos son los contenidos finales de los archivos principales modificados o creados en Sprint 2. Use esta sección **solo al final**, después de seguir el proceso.

## `app/config.py`
```python
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
```

## `app/__init__.py`
```python
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError

from app.config import Config
from app.errores import ErrorAPI

API_VERSION = "v1"

db = SQLAlchemy()
migrate = Migrate()


def create_app(configuracion=None):
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if configuracion:
        app.config.update(configuracion)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config["CORS_ALLOWED_ORIGINS"])

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "service": "alojamientos-api",
            "version": API_VERSION,
        }, 200

    # Importar los modelos permite que Alembic detecte sus tablas.
    from app.dominios.usuarios import modelos  # noqa: F401
    from app.dominios.usuarios import controladores as usuarios_ctrl
    from app.dominios.usuarios.controladores import admin_bp, usuarios_bp
    from app.dominios.usuarios.servicios import UsuarioServicio

    usuarios_ctrl.usuario_servicio = UsuarioServicio(
        app.config["SECRET_KEY"],
        app.config["JWT_EXP_MINUTES"],
    )

    app.register_blueprint(
        usuarios_bp,
        url_prefix=f"/api/{API_VERSION}/usuarios",
    )
    app.register_blueprint(
        admin_bp,
        url_prefix=f"/api/{API_VERSION}/admin",
    )

    @app.errorhandler(ValidationError)
    def manejar_error_validacion(error):
        return {
            "success": False,
            "error": {
                "message": "Datos inválidos.",
                "details": error.messages,
            },
        }, 400

    @app.errorhandler(ErrorAPI)
    def manejar_error_api(error):
        return {
            "success": False,
            "error": {"message": str(error)},
        }, error.status_code

    return app
```

## `app/errores.py`
```python
class ErrorAPI(Exception):
    """Error controlado que se transforma en una respuesta HTTP."""

    def __init__(self, mensaje, status_code=400):
        super().__init__(mensaje)
        self.status_code = status_code
```

## `app/seguridad.py`
```python
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
```

## `app/dominios/usuarios/modelos.py`
```python
from datetime import datetime

from app import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    rol = db.Column(db.String(20), nullable=False, server_default="usuario")

    perfil = db.relationship(
        "PerfilUsuario",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "correo": self.correo,
            "rol": self.rol,
        }


class PerfilUsuario(db.Model):
    __tablename__ = "perfiles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    apellido = db.Column(db.String(50))
    telefono = db.Column(db.String(20))
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        unique=True,
    )

    usuario = db.relationship("Usuario", back_populates="perfil")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "telefono": self.telefono,
            "usuario_id": self.usuario_id,
        }
```

## `app/dominios/usuarios/dtos.py`
```python
from marshmallow import Schema, fields, validate


class RegistroUsuarioDTO(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=6),
    )


class LoginUsuarioDTO(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(required=True, load_only=True)
```

## `app/dominios/usuarios/repositorios.py`
```python
from app import db
from app.dominios.usuarios.modelos import PerfilUsuario, Usuario


class UsuarioRepositorio:
    @staticmethod
    def guardar(usuario):
        db.session.add(usuario)
        db.session.commit()
        return usuario

    @staticmethod
    def obtener_por_correo(correo):
        return db.session.query(Usuario).filter_by(correo=correo).first()

    @staticmethod
    def obtener_por_id(usuario_id):
        return db.session.get(Usuario, usuario_id)

    @staticmethod
    def obtener_perfil(usuario_id):
        return (
            db.session.query(PerfilUsuario)
            .filter_by(usuario_id=usuario_id)
            .first()
        )

    @staticmethod
    def listar_todos():
        return db.session.query(Usuario).all()
```

## `app/dominios/usuarios/servicios.py`
```python
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
```

## `app/dominios/usuarios/controladores.py`
```python
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
```

## `tests/conftest.py`
```python
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
```

## `tests/test_usuarios.py`
```python
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
```

## `scripts/promover_admin.py`
```python
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
```

El archivo `tests/test_health.py` debe permanecer **exactamente igual al Sprint 1**. No reduzca ni elimine esos tests.