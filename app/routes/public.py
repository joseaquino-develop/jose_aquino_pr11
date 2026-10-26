import re
import unicodedata

from flask import (
    Blueprint,
    abort,
    jsonify,
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
from app.services import noticia_service
from app.database import db
from sqlalchemy.exc import SQLAlchemyError
from app.conexion_mysql import guardar_mensaje, obtener_aliados, obtener_noticias


public_bp = Blueprint(
    "public",
    __name__
)

CHATBOT_MONTHS = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)

CHATBOT_PRODUCTS = {
    "hass": ("hass",),
    "fuerte": ("fuerte",),
    "pecana": ("pecana",),
    "pallar": ("pallar",),
    "maiz-amarillo-duro": ("maiz", "maiz amarillo", "maiz duro"),
}


def _chatbot_season(key):
    harvest_months = [
        index
        for index, state in enumerate(TEMPORADAS.get(key, []))
        if state == "cosecha" and index < len(CHATBOT_MONTHS)
    ]
    if not harvest_months:
        return "por confirmar según campaña"

    return (
        f"{CHATBOT_MONTHS[harvest_months[0]]} a "
        f"{CHATBOT_MONTHS[harvest_months[-1]]}"
    )


def _chatbot_result(text, action_label=None, endpoint=None, **values):
    result = {"reply": text}
    if action_label and endpoint:
        result["action"] = {
            "label": action_label,
            "href": url_for(endpoint, **values),
        }
    return result


def _chatbot_answer(message):
    query = unicodedata.normalize("NFKD", message.casefold())
    query = "".join(
        char for char in query
        if not unicodedata.combining(char)
    )
    query = re.sub(r"[^a-z0-9\s]", " ", query)
    query = " ".join(query.split())

    def includes(*terms):
        return any(term in query for term in terms)

    def includes_word(term):
        return term in query.split()

    product_key = next(
        (
            key
            for key, names in CHATBOT_PRODUCTS.items()
            if any(name in query for name in names)
        ),
        None,
    )
    asks_season = includes(
        "temporada", "cosecha", "siembra", "disponibilidad",
        "disponible", "campana", "stock",
    )

    if query in {"hola", "buenas", "buenos dias", "buenas tardes", "buenas noches"}:
        return _chatbot_result(
            "¡Hola! ¿Qué información necesitas sobre Central Chavalina?",
            "Ver nuestros productos",
            "public.producto",
            key="hass",
        )

    if includes("horario", "horarios", "a que hora", "abren", "atienden"):
        return _chatbot_result(
            "Nuestro horario de atención es de lunes a viernes, de 8:00 a. m. a 6:00 p. m.",
            "Ir a contacto",
            "public.contacto",
        )

    if includes(
        "cotizacion", "cotizar", "cotiza", "precio", "precios",
        "costo", "comprar", "pedido", "pedir",
    ):
        return _chatbot_result(
            "Puedes completar el formulario de cotización o comunicarte por WhatsApp comercial. Te responderemos en menos de 24 horas.",
            "Solicitar cotización",
            "public.cotizacion",
        )

    if includes(
        "contacto", "contactar", "telefono", "celular", "whatsapp",
        "correo", "email", "llamar", "comunicar",
    ):
        return _chatbot_result(
            "Puedes escribirnos por WhatsApp al +51 912 237 268 o al correo contacto@centralchavalina.com. También puedes consultar el horario y los demás canales de atención en nuestra página de contacto.",
            "Ver canales de contacto",
            "public.contacto",
        )

    if includes(
        "ubicacion", "direccion", "donde estan", "donde queda",
        "mapa", "llegar", "san jose",
    ) or includes_word("ica"):
        return _chatbot_result(
            "La cooperativa está en el caserío Chavalina, distrito de San José de los Molinos, provincia y departamento de Ica, Perú.",
            "Ver ubicación y contacto",
            "public.contacto",
        )

    if includes(
        "certificacion", "certificaciones", "senasa", "globalgap",
        "globalg a p", "haccp", "bpa", "certificado",
    ):
        return _chatbot_result(
            "Sí, trabajamos con certificaciones de Buenas Prácticas Agrícolas y garantizamos trazabilidad y comercio justo para todos nuestros socios.",
            "Ver certificaciones",
            "public.certificaciones",
        )

    if asks_season and includes("palta", "paltas", "aguacate", "aguacates"):
        return _chatbot_result(
            "La campaña de Palta Hass y Fuerte se concentra de marzo a agosto. Te recomendamos contactarnos con anticipación para programar pedidos.",
            "Consultar disponibilidad",
            "public.disponibilidad",
        )

    if product_key and asks_season:
        product = PRODUCTS[product_key]
        return _chatbot_result(
            f"{product['name']}: la temporada publicada es {_chatbot_season(product_key)}. La disponibilidad y el volumen pueden variar según la campaña; consúltalos antes de planificar un pedido.",
            "Consultar calendario agrícola",
            "public.disponibilidad",
        )

    if asks_season:
        seasons = "; ".join(
            f"{PRODUCTS[key]['name']}: {_chatbot_season(key)}"
            for key in CHATBOT_PRODUCTS
        )
        return _chatbot_result(
            f"El calendario publicado indica: {seasons}. La disponibilidad real debe confirmarse con el equipo.",
            "Consultar disponibilidad",
            "public.disponibilidad",
        )

    if includes("aliado", "aliados", "agroideas", "agroexportadora", "agronomo", "agronomos"):
        return _chatbot_result(
            "La cooperativa publica alianzas y acompañamiento de AGROIDEAS, SENASA, ingenieros agrónomos y una empresa agroexportadora aliada para la comercialización de palta.",
            "Conocer nuestros aliados",
            "public.aliados",
        )

    if includes(
        "responsabilidad", "social", "familias", "valores", "mision",
        "vision", "asociatividad", "sostenibilidad",
    ):
        return _chatbot_result(
            "Central Chavalina promueve el desarrollo socioeconómico y sostenible de sus productores asociados y sus familias mediante asistencia técnica, mejora de la calidad y comercialización justa.",
            "Conocer nuestra cooperativa",
            "public.quienes_somos",
        )

    if includes(
        "quienes", "quien es", "cooperativa", "historia", "socios",
        "productores", "fundacion",
    ):
        return _chatbot_result(
            "La Cooperativa Agraria de Usuarios Central Chavalina se constituyó en 2025 y está integrada por 30 productores de San José de los Molinos, Ica. Trabaja para fortalecer a sus socios y acercar sus productos a compradores nacionales e internacionales.",
            "Quiénes somos",
            "public.quienes_somos",
        )

    if includes("noticias", "novedades", "actualidad", "exportacion", "exportar"):
        return _chatbot_result(
            "En la sección de noticias se publican novedades sobre cosechas, certificaciones, alianzas y avances comerciales de la cooperativa.",
            "Ver noticias",
            "public.noticias",
        )

    if product_key:
        product = PRODUCTS[product_key]
        return _chatbot_result(
            f"{product['name']}: {product['description']} Presentación: {product['presentation']}. Temporada publicada: {_chatbot_season(product_key)}. {product['volume']}",
            "Ver ficha del producto",
            "public.producto",
            key=product_key,
        )

    if includes("producto", "productos", "cultivo", "cultivos", "venden", "ofrecen", "catalogo"):
        product_names = ", ".join(
            product["name"] for product in PRODUCTS.values()
        )
        return _chatbot_result(
            f"Nos especializamos en {product_names}, cultivados con altos estándares de calidad.",
            "Explorar productos",
            "public.producto",
            key="hass",
        )

    if includes("gracias", "muchas gracias"):
        return _chatbot_result(
            "¡Con gusto! Si necesitas más información, aquí puedes contactar directamente con la cooperativa.",
            "Contactar con Chavalina",
            "public.contacto",
        )

    return _chatbot_result(
        "Puedo orientarte sobre productos, temporadas, certificaciones, ubicación, contacto y cotizaciones. Si tu consulta es específica, nuestro equipo puede ayudarte directamente.",
        "Contactar con la cooperativa",
        "public.contacto",
    )


@public_bp.route("/api/chatbot", methods=["POST"])
def chatbot():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Envía un mensaje en formato JSON."), 400

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip() or len(message) > 500:
        return jsonify(error="El mensaje debe contener entre 1 y 500 caracteres."), 400

    return jsonify(_chatbot_answer(message.strip()))


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
@public_bp.route("/inicio")
def home():

    # Actualizamos las temporadas antes
    # de mostrar los productos
    actualizar_temporadas_productos()

    slides = [
        {
            "img": IMAGENES["inicio_carrusel_1"],
            "tag": "Cooperativa Agraria · San José de los Molinos, Ica",
            "title": "Desde Ica, cultivamos calidad y llevamos nuestros productos al mundo.",
            "sub": (
                "Cooperativa Agraria de Usuarios Central Chavalina — "
                "30 familias productoras comprometidas con la calidad, "
                "la sostenibilidad y el comercio justo."
            ),
        },
        {
            "img": IMAGENES["inicio_carrusel_2"],
            "tag": "Producto principal · Palta Hass",
            "title": "Palta Hass de calidad que nace de nuestra tierra.",
            "sub": (
                "Producida en Ica con asistencia técnica integral. Cajas "
                "de 4 kg, cosecha de febrero a mayo. Disponible para "
                "mercados nacionales e internacionales."
            ),
        },
        {
            "img": IMAGENES["inicio_carrusel_3"],
            "tag": "Est. 2025 · 30 socios productores",
            "title": (
                "Calidad que nace de nuestra tierra y crece con "
                "nuestros productores."
            ),
            "sub": (
                "Nuestro modelo asociativo conecta directamente a "
                "productores de Ica con compradores, agroexportadoras "
                "y mercados que valoran el origen."
            ),
        },
    ]

    return render_template(
        "public/home.html",

        # Productos
        products=PRODUCTS,

        # Imágenes administrables
        imagenes=IMAGENES,

        slides=slides,
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
    aliados_bd = []
    aliados_aviso = None

    try:
        aliados_bd = obtener_aliados()
    except Exception as e:
        current_app.logger.error(f"Error consultando aliados en BD: {e}")
        aliados_aviso = "No se pudo cargar información actualizada. Mostrando datos de respaldo."

        aliados_bd = [
            {
                "id": item.get("id"),
                "nombre": item.get("nombre", ""),
                "subtitulo": item.get("subtitulo", ""),
                "descripcion": item.get("descripcion", ""),
                "imagen": item.get("imagen", ""),
            }
            for item in ALIADOS
        ]

    if not aliados_bd and aliados_aviso is None:
        aliados_aviso = "No hay aliados registrados"

    return render_template(
        "public/aliados.html",
        aliados=aliados_bd,
        aliados_aviso=aliados_aviso,
        active_nav="aliados"
    )


# ==========================================================
# NOTICIAS
# ==========================================================

@public_bp.route("/noticias")
def noticias():
    noticias_bd = []
    noticias_aviso = None

    try:
        noticias_bd = obtener_noticias()
    except Exception as e:
        current_app.logger.error(f"Error consultando noticias en BD: {e}")
        noticias_aviso = "No se pudo cargar información actualizada en este momento."

    return render_template(
        "public/noticias.html",
        noticias=noticias_bd,
        noticias_aviso=noticias_aviso,
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

            contacto_service.crear_contacto({
                "nombre": nombre,
                "correo": correo,
                "asunto": asunto,
                "mensaje": mensaje,
                "ip_origen": request.remote_addr,
            })

            flash(
                "¡Mensaje enviado! Te responderemos lo antes posible.",
                "success"
            )

        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Error guardando mensaje de contacto")

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
