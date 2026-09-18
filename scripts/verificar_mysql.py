from sqlalchemy import text

from app import create_app, db


app = create_app()

with app.app_context():
    base_actual, version = db.session.execute(
        text("SELECT DATABASE(), VERSION()")
    ).one()

    print("Conexion MySQL correcta")
    print(f"Base de datos: {base_actual}")
    print(f"Version MySQL: {version}")