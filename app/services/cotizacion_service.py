from app.database import db
from app.models.cotizacion import Cotizacion


def obtener_cotizaciones():
    return Cotizacion.query.order_by(Cotizacion.creado_en.desc()).all()


def obtener_cotizacion(cotizacion_id):
    return Cotizacion.query.get_or_404(cotizacion_id)


def _certificaciones_desde_form(data):
    """El formulario público envía varias casillas 'certs' (checkbox múltiple)
    con el mismo name; el formulario administrativo envía un solo texto.
    Soportamos ambos casos.
    """
    certs_lista = data.getlist("certs") if hasattr(data, "getlist") else None
    if certs_lista:
        return ", ".join(certs_lista)
    return data.get("certificaciones", data.get("certs", ""))


def crear_cotizacion(data):
    cotizacion = Cotizacion(
        empresa=data.get("empresa"),
        contacto=data.get("contacto_nombre", data.get("contacto")),
        cargo=data.get("contacto_cargo", data.get("cargo")),
        pais=data.get("pais"),
        email=data.get("correo", data.get("email")),
        telefono=data.get("telefono"),
        web=data.get("pagina_web", data.get("web")),
        producto=data.get("producto"),
        cantidad=data.get("cantidad"),
        unidad=data.get("unidad"),
        frecuencia=data.get("frecuencia"),
        destino=data.get("destino"),
        incoterm=data.get("incoterm"),
        certificaciones=_certificaciones_desde_form(data),
        notas=data.get("notas"),
    )
    db.session.add(cotizacion)
    db.session.commit()
    return cotizacion


def actualizar_cotizacion(cotizacion_id, data):
    cotizacion = obtener_cotizacion(cotizacion_id)
    cotizacion.empresa = data.get("empresa", cotizacion.empresa)
    cotizacion.contacto = data.get(
        "contacto_nombre",
        data.get("contacto", cotizacion.contacto)
    )
    cotizacion.cargo = data.get(
        "contacto_cargo",
        data.get("cargo", cotizacion.cargo)
    )
    cotizacion.pais = data.get("pais", cotizacion.pais)
    cotizacion.email = data.get(
        "correo",
        data.get("email", cotizacion.email)
    )
    cotizacion.telefono = data.get("telefono", cotizacion.telefono)
    cotizacion.web = data.get(
        "pagina_web",
        data.get("web", cotizacion.web)
    )
    cotizacion.producto = data.get("producto", cotizacion.producto)
    cotizacion.cantidad = data.get("cantidad", cotizacion.cantidad)
    cotizacion.unidad = data.get("unidad", cotizacion.unidad)
    cotizacion.frecuencia = data.get("frecuencia", cotizacion.frecuencia)
    cotizacion.destino = data.get("destino", cotizacion.destino)
    cotizacion.incoterm = data.get("incoterm", cotizacion.incoterm)
    cotizacion.certificaciones = _certificaciones_desde_form(data) or cotizacion.certificaciones
    cotizacion.notas = data.get("notas", cotizacion.notas)
    db.session.commit()
    return cotizacion


def eliminar_cotizacion(cotizacion_id):
    cotizacion = obtener_cotizacion(cotizacion_id)
    db.session.delete(cotizacion)
    db.session.commit()