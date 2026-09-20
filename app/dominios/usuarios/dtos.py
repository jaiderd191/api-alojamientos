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