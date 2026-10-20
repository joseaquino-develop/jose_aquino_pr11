from flask import (
    Blueprint,
    abort,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
)

from app.data.products import OTHERS, PRODUCTS
from app.data.temporadas import TEMPORADAS
from app.data.imagenes import IMAGENES
from app.data.aliados import ALIADOS

from app.services import cotizacion_service, contacto_service
from app.conexion_mysql import guardar_mensaje


public_bp = Blueprint(
    "public",
    __name__
)


# ==========================================================
# MESES DEL AÑO
# ==========================================================

def _months():

    return [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic",
    ]


# ==========================================================
# CALCULAR TEMPORADA
# ==========================================================

def calcular_temporada(calendario):
    """
    Calcula automáticamente la temporada utilizando
    los meses marcados como cosecha.

    Ejemplo:
    Feb, Mar, Abr, May -> Feb – May
    """

    meses = _months()

    meses_cosecha = [
        i
        for i, estado in enumerate(calendario)
        if estado == "cosecha"
    ]

    # Si no existen meses de cosecha
    if not meses_cosecha:
        return "Consultar temporada"

    # Si solamente existe un mes de cosecha
    if len(meses_cosecha) == 1:
        return meses[meses_cosecha[0]]

    # Primer mes de cosecha
    primero = meses[meses_cosecha[0]]

    # Último mes de cosecha
    ultimo = meses[meses_cosecha[-1]]

    return f"{primero} – {ultimo}"


# ==========================================================
# ACTUALIZAR TEMPORADAS DE LOS PRODUCTOS
# ==========================================================

def actualizar_temporadas_productos():
    """
    Toma la información editable de temporadas.py
    y la aplica sobre PRODUCTS.

    De esta manera Productos y Disponibilidad utilizan
    exactamente el mismo calendario.
    """

    for key, producto in PRODUCTS.items():

        calendario = TEMPORADAS.get(
            key,
            producto.get(
                "calendar",
                ["none"] * 12
            )
        )

        # Protección por si algún calendario
        # no contiene exactamente 12 meses
        if len(calendario) != 12:
            calendario = ["none"] * 12

        producto["calendar"] = calendario

        producto["season"] = calcular_temporada(
            calendario
        )


# ==========================================================
# INICIO
# ==========================================================

@public_bp.route("/")
def home():

    # Actualizamos las temporadas antes
    # de mostrar los productos
    actualizar_temporadas_productos()

    return render_template(
        "public/home.html",

        # Productos
        products=PRODUCTS,

        # Imágenes administrables
        imagenes=IMAGENES,

        active_nav="inicio",
    )


# ==========================================================
# NOSOTROS
# ==========================================================

@public_bp.route("/nosotros")
def quienes_somos():

    return render_template(
        "public/nosotros/quienes_somos.html",
        active_nav="nosotros",
    )


# ==========================================================
# DISPONIBILIDAD
# ==========================================================

@public_bp.route("/nosotros/disponibilidad")
def disponibilidad():

    # Aplicar los cambios realizados
    # desde el panel administrador
    actualizar_temporadas_productos()

    return render_template(
        "public/nosotros/disponibilidad.html",
        products=PRODUCTS,
        months=_months(),
        active_nav="nosotros",
    )


# ==========================================================
# RESPONSABILIDAD
# ==========================================================

@public_bp.route("/nosotros/responsabilidad")
def responsabilidad():

    return render_template(
        "public/nosotros/responsabilidad.html",
        active_nav="nosotros",
    )


# ==========================================================
# CERTIFICACIONES
# ==========================================================

@public_bp.route("/nosotros/certificaciones")
def certificaciones():

    return render_template(
        "public/nosotros/certificaciones.html",
        active_nav="nosotros",
    )


# ==========================================================
# PRODUCTOS
# ==========================================================

@public_bp.route("/productos/<key>")
def producto(key):

    # Primero aplicamos la información
    # guardada en temporadas.py
    actualizar_temporadas_productos()

    p = PRODUCTS.get(key)

    # Producto no encontrado
    if not p:
        abort(404)

    # Obtener productos relacionados
    otros_productos = OTHERS.get(
        key,
        []
    )

    return render_template(
        "public/producto.html",
        p=p,
        products=PRODUCTS,
        months=_months(),
        others=otros_productos,
        active_nav="productos",
    )


# ==========================================================
# ALIADOS
# ==========================================================

@public_bp.route("/aliados")
def aliados():
    return render_template(
        "public/aliados.html",
        aliados=ALIADOS,
        active_nav="aliados"
    )


# ==========================================================
# NOTICIAS
# ==========================================================

@public_bp.route("/noticias")
def noticias():

    return render_template(
        "public/noticias.html",
        active_nav="noticias",
    )


# ==========================================================
# CONTACTO
# ==========================================================

@public_bp.route(
    "/contacto",
    methods=["GET", "POST"]
)
def contacto():

    if request.method == "POST":

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        correo = request.form.get(
            "correo",
            ""
        ).strip()

        asunto = request.form.get(
            "asunto",
            ""
        ).strip()

        mensaje = request.form.get(
            "mensaje",
            ""
        ).strip()

        # Validación básica
        if (
            not nombre
            or not mensaje
            or "@" not in correo
        ):

            flash(
                "Completa tu nombre, un correo válido y el mensaje.",
                "danger"
            )

            return redirect(
                url_for("public.contacto")
            )

        try:

            guardar_mensaje(
                nombre,
                correo,
                asunto,
                mensaje,
                request.remote_addr
            )

            flash(
                "¡Mensaje enviado! Te responderemos lo antes posible.",
                "success"
            )

        except Exception as e:

            current_app.logger.error(
                f"Error guardando mensaje de contacto: {e}"
            )

            flash(
                "No pudimos enviar tu mensaje. Inténtalo más tarde.",
                "danger"
            )

        return redirect(
            url_for("public.contacto")
        )

    return render_template(
        "public/contacto.html",
        active_nav="contacto"
    )


# ==========================================================
# COTIZACIÓN
# ==========================================================

@public_bp.route(
    "/cotizacion",
    methods=["GET", "POST"]
)
def cotizacion():

    enviado = False

    if request.method == "POST":

        # Si los datos llegan mediante formulario
        if request.form:

            form_data = request.form.to_dict(
                flat=False
            )

            data = {
                k: (
                    ", ".join(v)
                    if len(v) > 1
                    else v[0]
                )
                for k, v in form_data.items()
            }

        # Si llegan como JSON
        else:

            data = (
                request.get_json(
                    silent=True
                )
                or {}
            )

        print(
            "DATOS RECIBIDOS EN /cotizacion:",
            data
        )

        cotizacion_service.crear_cotizacion(
            data
        )

        enviado = True

    return render_template(
        "public/cotizacion.html",
        enviado=enviado,
        active_nav="cotizacion",
    )
