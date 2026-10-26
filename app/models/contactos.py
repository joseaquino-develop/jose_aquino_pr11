from app.database import db


class Contacto(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column("name", db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    asunto = db.Column("subject", db.String(255), nullable=True)
    mensaje = db.Column("message", db.Text, nullable=False)
    ip_origen = db.Column("origin_ip", db.String(45), nullable=True)
    creado_en = db.Column("created_at", db.DateTime, server_default=db.func.now())