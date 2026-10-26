from app.database import db
from app.models.noticia import Noticia


def obtener_noticias():
    return Noticia.query.order_by(Noticia.id.desc()).all()


def obtener_noticia(noticia_id):
    return Noticia.query.get_or_404(noticia_id)


def crear_noticia(data):
    noticia = Noticia(
        categoria=data["categoria"],
        fecha=data["fecha"],
        titulo=data["titulo"],
        resumen=data["resumen"],
        imagen=data.get("imagen") or None,
    )
    db.session.add(noticia)
    db.session.commit()
    return noticia


def actualizar_noticia(noticia, data):
    noticia.categoria = data["categoria"]
    noticia.fecha = data["fecha"]
    noticia.titulo = data["titulo"]
    noticia.resumen = data["resumen"]
    if data.get("imagen"):
        noticia.imagen = data["imagen"]

    db.session.commit()
    return noticia


def eliminar_noticia(noticia):
    db.session.delete(noticia)
    db.session.commit()
