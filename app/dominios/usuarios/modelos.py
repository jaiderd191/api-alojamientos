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