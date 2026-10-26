from app.database import db
from app.models.contactos import Contacto

def crear_contacto(data):
    contacto = Contacto(
        nombre=data.get("nombre"),
        email=data.get("correo", data.get("email")),
        asunto=data.get("asunto"),
        mensaje=data.get("mensaje"),
        ip_origen=data.get("ip_origen")
    )
    db.session.add(contacto)
    db.session.commit()
    return contacto