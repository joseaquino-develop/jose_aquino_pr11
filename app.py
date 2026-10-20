
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import (
    send_from_directory,
    request,
    redirect,
    url_for,
    flash,
    render_template,
    session,
)
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash
import mysql.connector

# Cargar las variables del archivo .env
load_dotenv(override=True)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "chavalina_app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cotizaciones_db")

# Configuración de conexión MySQL
DB_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "connection_timeout": 5,
}

# Construir la aplicación Flask
from app import create_app

app = create_app()

if not app.secret_key:
    app.secret_key = os.getenv(
        "SECRET_KEY",
        "clave-local-desarrollo",
    )

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1,
)


def limpiar(valor):
    """Quita espacios y devuelve None si el campo está vacío."""
    if valor is None:
        return None

    valor = valor.strip()
    return valor if valor else None


# ==========================================
# SITEMAP
# ==========================================

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(
        app.static_folder,
        "sitemap.xml",
        mimetype="application/xml",
    )


# ==========================================
# LOGIN DEL ADMINISTRADOR
# ==========================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        usuario = limpiar(request.form.get("usuario"))
        password = request.form.get("password", "")

        conexion = None
        cursor = None

        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM usuarios WHERE usuario = %s",
                (usuario,),
            )
            user = cursor.fetchone()

            if user and check_password_hash(user["password"], password):
                session["admin"] = True
                session["usuario"] = user["usuario"]
                return redirect(url_for("admin.dashboard"))

            return render_template(
                "admin/login.html",
                error="Usuario o contraseña incorrectos.",
            )

        except mysql.connector.Error:
            app.logger.exception("Error al iniciar sesión")
            return render_template(
                "admin/login.html",
                error="Error de conexión con la base de datos.",
            )

        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    return render_template("admin/login.html")


# ==========================================
# GUARDAR COTIZACIONES
# ==========================================

@app.route("/enviar-cotizacion", methods=["POST"])
def enviar_cotizacion():
    empresa = limpiar(request.form.get("empresa"))
    contacto_nombre = limpiar(request.form.get("contacto_nombre"))
    contacto_cargo = limpiar(request.form.get("contacto_cargo"))
    pais = limpiar(request.form.get("pais"))
    correo = limpiar(request.form.get("correo"))
    telefono = limpiar(request.form.get("telefono"))
    pagina_web = limpiar(request.form.get("pagina_web"))

    producto = limpiar(request.form.get("producto"))
    cantidad = limpiar(request.form.get("cantidad"))
    unidad = limpiar(request.form.get("unidad"))
    frecuencia = limpiar(request.form.get("frecuencia"))
    destino = limpiar(request.form.get("destino"))

    incoterm = limpiar(request.form.get("incoterm"))
    certificaciones_lista = request.form.getlist("certificaciones")
    certificaciones = (
        ", ".join(certificaciones_lista)
        if certificaciones_lista
        else "Ninguna"
    )
    notas = limpiar(request.form.get("notas"))

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
            "Faltan campos obligatorios. Revisa el formulario.",
            "error",
        )
        return redirect(url_for("public.cotizacion"))

    conexion = None
    cursor = None

    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        query = """
            INSERT INTO cotizaciones (
                empresa,
                contacto,
                cargo,
                pais,
                email,
                telefono,
                web,
                producto,
                cantidad,
                unidad,
                frecuencia,
                destino,
                incoterm,
                certificaciones,
                notas
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """

        valores = (
            empresa,
            contacto_nombre,
            contacto_cargo,
            pais,
            correo,
            telefono or "",
            pagina_web,
            producto,
            cantidad,
            unidad,
            frecuencia,
            destino,
            incoterm,
            certificaciones,
            notas,
        )

        cursor.execute(query, valores)
        conexion.commit()

        flash("¡Cotización enviada correctamente!", "success")

    except mysql.connector.Error:
        if conexion and conexion.is_connected():
            conexion.rollback()

        app.logger.exception("Error al guardar la cotización")
        flash(
            "Hubo un error al procesar tu cotización. Revisa la base de datos.",
            "error",
        )

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return redirect(url_for("public.cotizacion", enviado=1))


# ==========================================
# GUARDAR MENSAJES DE CONTACTO
# ==========================================

@app.route("/enviar-contacto", methods=["POST"])
def enviar_contacto():
    nombre = limpiar(request.form.get("nombre"))
    correo = limpiar(request.form.get("correo"))
    asunto = limpiar(request.form.get("asunto"))
    mensaje = limpiar(request.form.get("mensaje"))

    if not all([nombre, correo, mensaje]):
        flash(
            "Completa nombre, correo y mensaje.",
            "error",
        )
        return redirect(url_for("public.contacto"))

    conexion = None
    cursor = None

    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        query = """
            INSERT INTO contactos (nombre, email, asunto, mensaje)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (nombre, correo, asunto, mensaje),
        )
        conexion.commit()

        flash("¡Mensaje enviado correctamente!", "success")

    except mysql.connector.Error:
        if conexion and conexion.is_connected():
            conexion.rollback()

        app.logger.exception("Error al guardar el mensaje de contacto")
        flash(
            "Hubo un error al enviar el mensaje.",
            "error",
        )

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return redirect(url_for("public.contacto"))


# ==========================================
# INICIAR APLICACIÓN
# ==========================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
