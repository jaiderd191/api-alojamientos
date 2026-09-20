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