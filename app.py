
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv(override=True)

from app import create_app
from app.database import db
from app.services import contacto_service, cotizacion_service
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import (
    current_app,
    send_from_directory,
    request,
    redirect,
    url_for,
    flash,
)
from sqlalchemy.exc import SQLAlchemyError


# ==========================================
# CREAR LA APLICACIÓN
# ==========================================
app = create_app()


# Configurar la clave secreta
if not app.secret_key:
    app.secret_key = os.environ.get(
        "SECRET_KEY",
        "cambia-esta-clave-en-produccion"
    )


# Recargar las plantillas HTML al modificarlas
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True


# Configurar el proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1,
)


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def limpiar(valor):
    """Quita espacios y devuelve None si el campo está vacío."""
    if valor is None:
        return None

    valor = valor.strip()
    return valor if valor else None


# ==========================================
# RUTA DEL SITEMAP
# ==========================================
@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(
        os.path.dirname(os.path.abspath(__file__)),
        "sitemap.xml",
        mimetype="application/xml",
    )


# ==========================================
# RUTAS PÚBLICAS ANTIGUAS
# ==========================================
@app.route("/login", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
@app.route("/admin/register", methods=["GET", "POST"])
def acceso_publico_antiguo():
    return redirect(url_for("public.home"))


# ==========================================
# PROCESAR FORMULARIO DE COTIZACIÓN
# ==========================================
@app.route("/enviar-cotizacion", methods=["POST"])
def enviar_cotizacion():
    """Recoge y guarda una solicitud de cotización."""

    # Empresa y contacto
    empresa = limpiar(request.form.get("empresa"))
    contacto_nombre = limpiar(
        request.form.get(
            "contacto_nombre",
            request.form.get("contacto"),
        )
    )
    contacto_cargo = limpiar(
        request.form.get(
            "contacto_cargo",
            request.form.get("cargo"),
        )
    )
    pais = limpiar(request.form.get("pais"))
    correo = limpiar(
        request.form.get("correo", request.form.get("email"))
    )
    telefono = limpiar(request.form.get("telefono"))
    pagina_web = limpiar(
        request.form.get(
            "pagina_web",
            request.form.get("web"),
        )
    )

    # Producto y volumen
    producto = limpiar(request.form.get("producto"))
    cantidad = limpiar(request.form.get("cantidad"))
    unidad = limpiar(request.form.get("unidad"))
    frecuencia = limpiar(request.form.get("frecuencia"))
    destino = limpiar(request.form.get("destino"))

    # Condiciones comerciales
    incoterm = limpiar(request.form.get("incoterm"))
    certificaciones_list = request.form.getlist("certificaciones")
    certificaciones = (
        ", ".join(certificaciones_list)
        if certificaciones_list
        else "Ninguna"
    )
    notas = limpiar(request.form.get("notas"))

    # Validar campos obligatorios
    obligatorios = [
        empresa,
        contacto_nombre,
        pais,
        correo,
        producto,
        cantidad,
        incoterm,
    ]

    if not all(obligatorios):
        flash(
            "Faltan campos obligatorios. "
            "Revisa el formulario e inténtalo de nuevo.",
            "error",
        )
        return redirect(url_for("public.cotizacion"))

    try:
        cotizacion_service.crear_cotizacion({
            "empresa": empresa,
            "contacto_nombre": contacto_nombre,
            "contacto_cargo": contacto_cargo,
            "pais": pais,
            "correo": correo,
            "telefono": telefono,
            "pagina_web": pagina_web,
            "producto": producto,
            "cantidad": cantidad,
            "unidad": unidad,
            "frecuencia": frecuencia,
            "destino": destino,
            "incoterm": incoterm,
            "certificaciones": certificaciones,
            "notas": notas,
        })

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception(
            "Error al guardar cotización"
        )
        flash(
            "Hubo un error al procesar tu cotización. "
            "Inténtalo nuevamente.",
            "error",
        )
        return redirect(url_for("public.cotizacion"))

    return redirect(
        url_for("public.cotizacion", enviado=1)
    )


# ==========================================
# PROCESAR FORMULARIO DE CONTACTO
# ==========================================
@app.route("/enviar-contacto", methods=["POST"])
def enviar_contacto():
    """Recoge y guarda un mensaje de contacto."""

    nombre = limpiar(request.form.get("nombre"))
    correo = limpiar(request.form.get("correo"))
    asunto = limpiar(request.form.get("asunto"))
    mensaje = limpiar(request.form.get("mensaje"))

    if not all([nombre, correo, mensaje]):
        flash(
            "Completa nombre, correo y mensaje para poder enviarlo.",
            "error",
        )
        return redirect(url_for("public.contacto"))

    try:
        contacto_service.crear_contacto({
            "nombre": nombre,
            "correo": correo,
            "asunto": asunto,
            "mensaje": mensaje,
            "ip_origen": request.remote_addr,
        })

        flash(
            "¡Mensaje enviado correctamente!",
            "success",
        )

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception(
            "Error al guardar mensaje de contacto"
        )
        flash(
            "Hubo un error al enviar tu mensaje.",
            "error",
        )

    return redirect(url_for("public.contacto"))


# ==========================================
# INICIAR APLICACIÓN
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
