import os
import time
import uuid

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
    current_app,
    flash,
)

from werkzeug.utils import secure_filename

from app.auth import admin_required
from app.database import db
from app.data.products import PRODUCTS
from app.data.temporadas import TEMPORADAS
from app.data.imagenes import IMAGENES
from app.data.aliados import ALIADOS
from app.models.cotizacion import Cotizacion
from app.models.contactos import Contacto
from app.services import noticia_service


# ==========================================================
# CONFIGURACIÓN DE IMÁGENES
# ==========================================================

EXTENSIONES_PERMITIDAS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}

NOMBRES_IMAGENES = {
    "inicio_carrusel_1": "Carrusel 1",
    "inicio_carrusel_2": "Carrusel 2",
    "inicio_carrusel_3": "Carrusel 3",
    "inicio_nosotros": "Quiénes somos",
    "inicio_responsabilidad": "Responsabilidad Social",
}


# ==========================================================
# FUNCIONES PARA LAS TEMPORADAS
# ==========================================================

def calcular_temporada(calendario):

    meses = [
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

    meses_cosecha = [
        i
        for i, estado in enumerate(calendario)
        if estado == "cosecha"
    ]

    if not meses_cosecha:
        return "Consultar temporada"

    if len(meses_cosecha) == 1:
        return meses[meses_cosecha[0]]

    primero = meses[meses_cosecha[0]]
    ultimo = meses[meses_cosecha[-1]]

    return f"{primero} – {ultimo}"


def guardar_temporadas():

    ruta = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "temporadas.py",
        )
    )

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            '"""Temporadas y calendario agrícola '
            'de los productos de Chavalina."""\n\n'
        )

        archivo.write("TEMPORADAS = {\n")

        for key, calendario in TEMPORADAS.items():

            archivo.write(
                f'    "{key}": [\n'
            )

            for estado in calendario:

                archivo.write(
                    f'        "{estado}",\n'
                )

            archivo.write("    ],\n\n")

        archivo.write("}\n")


# ==========================================================
# FUNCIONES PARA LAS IMÁGENES
# ==========================================================

def extension_permitida(nombre_archivo):

    return (
        "." in nombre_archivo
        and nombre_archivo
        .rsplit(".", 1)[1]
        .lower()
        in EXTENSIONES_PERMITIDAS
    )


def guardar_configuracion_imagenes():
    """
    Guarda las rutas actuales de las imágenes
    dentro de app/data/imagenes.py.
    """

    ruta = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "imagenes.py",
        )
    )

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            '"""Configuración de imágenes '
            'editables de la página web."""\n\n'
        )

        archivo.write("IMAGENES = {\n")

        for key, valor in IMAGENES.items():

            archivo.write(
                f'    {key!r}: {valor!r},\n'
            )

        archivo.write("}\n")

# ==========================================================
# FUNCIONES PARA LOS ALIADOS
# ==========================================================

def guardar_aliados():
    """
    Guarda la información actual de los aliados
    dentro de app/data/aliados.py.
    """

    ruta = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "aliados.py",
        )
    )

    with open(ruta, "w", encoding="utf-8") as archivo:

        archivo.write(
            '"""Información editable de los aliados '
            'estratégicos de Chavalina."""\n\n'
        )

        archivo.write("ALIADOS = ")

        archivo.write(
            repr(ALIADOS)
        )

        archivo.write("\n")

# ==========================================================
# BLUEPRINT DEL ADMINISTRADOR
# ==========================================================

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)


# ==========================================================
# CERRAR SESIÓN
# ==========================================================

@dashboard_bp.route("/logout")
@admin_required
def logout():
    # Esta ruta GET se conserva para compatibilidad con enlaces antiguos.
    session.clear()

    return redirect(
        url_for("authentication.admin_login")
    )


# ==========================================================
# DASHBOARD PRINCIPAL
# ==========================================================

@dashboard_bp.route("")
@dashboard_bp.route("/")
@admin_required
def index():

    total_productos = len(PRODUCTS)

    total_cotizaciones = (
        Cotizacion.query.count()
    )

    total_contactos = (
        Contacto.query.count()
    )

    ultimas_cotizaciones = (
        Cotizacion.query
        .order_by(Cotizacion.id.desc())
        .limit(5)
        .all()
    )

    ultimos_contactos = (
        Contacto.query
        .order_by(Contacto.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_productos=total_productos,
        total_cotizaciones=total_cotizaciones,
        total_contactos=total_contactos,
        ultimas_cotizaciones=ultimas_cotizaciones,
        ultimos_contactos=ultimos_contactos
    )


# ==========================================================
# TODAS LAS COTIZACIONES
# ==========================================================

@dashboard_bp.route("/cotizaciones")
@admin_required
def cotizaciones():

    cotizaciones = (
        Cotizacion.query
        .order_by(Cotizacion.id.desc())
        .all()
    )

    return render_template(
        "admin/cotizaciones.html",
        cotizaciones=cotizaciones
    )


# ==========================================================
# DETALLE DE UNA COTIZACIÓN
# ==========================================================

@dashboard_bp.route(
    "/cotizaciones/<int:id>"
)
@admin_required
def detalle_cotizacion(id):

    cotizacion = (
        Cotizacion.query.get_or_404(id)
    )

    return render_template(
        "admin/detalle_cotizacion.html",
        cotizacion=cotizacion
    )


# ==========================================================
# ELIMINAR COTIZACIÓN
# ==========================================================

@dashboard_bp.route(
    "/cotizaciones/<int:id>/eliminar",
    methods=["POST"]
)
@admin_required
def eliminar_cotizacion(id):

    cotizacion = (
        Cotizacion.query.get_or_404(id)
    )

    db.session.delete(cotizacion)
    db.session.commit()

    return redirect(
        url_for("dashboard.cotizaciones")
    )


# ==========================================================
# TODOS LOS CONTACTOS
# ==========================================================

@dashboard_bp.route("/contactos")
@admin_required
def contactos():

    contactos = (
        Contacto.query
        .order_by(Contacto.id.desc())
        .all()
    )

    return render_template(
        "admin/contactos.html",
        contactos=contactos
    )


# ==========================================================
# DETALLE DE UN CONTACTO
# ==========================================================

@dashboard_bp.route(
    "/contactos/<int:id>"
)
@admin_required
def detalle_contacto(id):

    contacto = (
        Contacto.query.get_or_404(id)
    )

    return render_template(
        "admin/detalle_contacto.html",
        contacto=contacto
    )


# ==========================================================
# ELIMINAR CONTACTO
# ==========================================================

@dashboard_bp.route(
    "/contactos/<int:id>/eliminar",
    methods=["POST"]
)
@admin_required
def eliminar_contacto(id):

    contacto = (
        Contacto.query.get_or_404(id)
    )

    db.session.delete(contacto)
    db.session.commit()

    return redirect(
        url_for("dashboard.contactos")
    )


# ==========================================================
# TODOS LOS PRODUCTOS
# ==========================================================

@dashboard_bp.route("/productos")
@admin_required
def productos():

    for key, producto in PRODUCTS.items():

        calendario = TEMPORADAS.get(
            key,
            producto.get(
                "calendar",
                ["none"] * 12
            )
        )

        producto["calendar"] = calendario

        producto["season"] = (
            calcular_temporada(calendario)
        )

    return render_template(
        "admin/lista_productos.html",
        products=PRODUCTS
    )


# ==========================================================
# EDITAR TEMPORADA DE UN PRODUCTO
# ==========================================================

@dashboard_bp.route(
    "/productos/<key>",
    methods=["GET", "POST"]
)
@admin_required
def detalle_producto(key):

    producto = PRODUCTS.get(key)

    if not producto:

        return redirect(
            url_for("dashboard.productos")
        )

    calendario = TEMPORADAS.get(
        key,
        producto.get(
            "calendar",
            ["none"] * 12
        )
    )

    if request.method == "POST":

        nuevo_calendario = []

        for i in range(12):

            estado = request.form.get(
                f"mes_{i}",
                "none"
            )

            if estado not in (
                "none",
                "siembra",
                "cosecha"
            ):

                estado = "none"

            nuevo_calendario.append(
                estado
            )

        TEMPORADAS[key] = nuevo_calendario

        guardar_temporadas()

        producto["calendar"] = (
            nuevo_calendario
        )

        producto["season"] = (
            calcular_temporada(
                nuevo_calendario
            )
        )

        return redirect(
            url_for(
                "dashboard.detalle_producto",
                key=key
            )
        )

    producto["calendar"] = calendario

    producto["season"] = (
        calcular_temporada(calendario)
    )

    return render_template(
        "admin/detalle_producto.html",
        producto=producto
    )


# ==========================================================
# ADMINISTRAR IMÁGENES DE INICIO
# ==========================================================

@dashboard_bp.route("/imagenes")
@admin_required
def imagenes():

    return render_template(
        "admin/imagenes.html",
        imagenes=IMAGENES,
        nombres=NOMBRES_IMAGENES,
    )


# ==========================================================
# CAMBIAR IMAGEN
# ==========================================================

@dashboard_bp.route(
    "/imagenes/<key>",
    methods=["POST"]
)
@admin_required
def cambiar_imagen(key):

    # Comprobar que la imagen existe
    if key not in IMAGENES:

        flash(
            "La imagen seleccionada no existe.",
            "danger"
        )

        return redirect(
            url_for("dashboard.imagenes")
        )

    # Obtener archivo
    archivo = request.files.get(
        "imagen"
    )

    # Comprobar que se seleccionó una imagen
    if (
        not archivo
        or archivo.filename == ""
    ):

        flash(
            "Selecciona una imagen.",
            "danger"
        )

        return redirect(
            url_for("dashboard.imagenes")
        )

    # Validar formato
    if not extension_permitida(
        archivo.filename
    ):

        flash(
            "Solo se permiten imágenes JPG, JPEG, PNG o WEBP.",
            "danger"
        )

        return redirect(
            url_for("dashboard.imagenes")
        )

    # Obtener extensión
    extension = (
        archivo.filename
        .rsplit(".", 1)[1]
        .lower()
    )

    # Crear nombre único
    marca_tiempo = int(
        time.time()
    )

    nombre_archivo = secure_filename(
        f"{key}_{marca_tiempo}.{extension}"
    )

    # Carpeta:
    # app/static/uploads
    carpeta_uploads = os.path.join(
        current_app.static_folder,
        "uploads"
    )

    os.makedirs(
        carpeta_uploads,
        exist_ok=True
    )

    ruta_archivo = os.path.join(
        carpeta_uploads,
        nombre_archivo
    )

    # Guardar físicamente la imagen
    archivo.save(
        ruta_archivo
    )

    # Ruta pública
    nueva_ruta = (
        f"/static/uploads/{nombre_archivo}"
    )

    # Actualizar configuración
    IMAGENES[key] = nueva_ruta

    # Guardar en imagenes.py
    guardar_configuracion_imagenes()

    flash(
        "Imagen actualizada correctamente.",
        "success"
    )

    return redirect(
        url_for("dashboard.imagenes")
    )

# ==========================================================
# ADMINISTRAR NOTICIAS
# ==========================================================

@dashboard_bp.route("/noticias")
@admin_required
def noticias():
    return render_template(
        "admin/noticias.html",
        noticias=noticia_service.obtener_noticias(),
    )


def _datos_noticia_desde_formulario():
    return {
        "categoria": request.form.get("categoria", "").strip(),
        "fecha": request.form.get("fecha", "").strip(),
        "titulo": request.form.get("titulo", "").strip(),
        "resumen": request.form.get("resumen", "").strip(),
    }


def _guardar_imagen_noticia(archivo):
    if not archivo or not archivo.filename:
        return None

    if not extension_permitida(archivo.filename):
        raise ValueError("Solo se permiten imágenes JPG, JPEG, PNG o WEBP.")

    extension = archivo.filename.rsplit(".", 1)[1].lower()
    nombre_archivo = f"noticia_{uuid.uuid4().hex}.{extension}"
    carpeta_imagenes = os.path.join(current_app.static_folder, "img", "noticias")
    os.makedirs(carpeta_imagenes, exist_ok=True)
    archivo.save(os.path.join(carpeta_imagenes, nombre_archivo))
    return f"img/noticias/{nombre_archivo}"


def _validar_datos_noticia(data):
    return all(
        data.get(campo)
        for campo in ("categoria", "fecha", "titulo", "resumen")
    )


@dashboard_bp.route("/noticias/nueva", methods=["GET", "POST"])
@admin_required
def nueva_noticia():
    if request.method == "POST":
        data = _datos_noticia_desde_formulario()
        if not _validar_datos_noticia(data):
            flash("Completa todos los campos obligatorios.", "danger")
            return render_template(
                "admin/form_noticia.html",
                noticia=None,
                titulo="Nueva noticia",
            ), 400

        try:
            data["imagen"] = _guardar_imagen_noticia(
                request.files.get("imagen")
            )
        except ValueError as error:
            flash(str(error), "danger")
            return render_template(
                "admin/form_noticia.html",
                noticia=None,
                titulo="Nueva noticia",
            ), 400

        noticia_service.crear_noticia(data)
        flash("Noticia creada correctamente.", "success")
        return redirect(url_for("dashboard.noticias"))

    return render_template(
        "admin/form_noticia.html",
        noticia=None,
        titulo="Nueva noticia",
    )


@dashboard_bp.route(
    "/noticias/<int:noticia_id>/editar",
    methods=["GET", "POST"],
)
@admin_required
def editar_noticia(noticia_id):
    noticia = noticia_service.obtener_noticia(noticia_id)

    if request.method == "POST":
        data = _datos_noticia_desde_formulario()
        if not _validar_datos_noticia(data):
            flash("Completa todos los campos obligatorios.", "danger")
            return render_template(
                "admin/form_noticia.html",
                noticia=noticia,
                titulo="Editar noticia",
            ), 400

        try:
            data["imagen"] = _guardar_imagen_noticia(
                request.files.get("imagen")
            )
        except ValueError as error:
            flash(str(error), "danger")
            return render_template(
                "admin/form_noticia.html",
                noticia=noticia,
                titulo="Editar noticia",
            ), 400

        noticia_service.actualizar_noticia(noticia, data)
        flash("Noticia actualizada correctamente.", "success")
        return redirect(url_for("dashboard.noticias"))

    return render_template(
        "admin/form_noticia.html",
        noticia=noticia,
        titulo="Editar noticia",
    )


@dashboard_bp.route(
    "/noticias/<int:noticia_id>/eliminar",
    methods=["POST"],
)
@admin_required
def eliminar_noticia(noticia_id):
    noticia = noticia_service.obtener_noticia(noticia_id)
    noticia_service.eliminar_noticia(noticia)
    flash("Noticia eliminada correctamente.", "success")
    return redirect(url_for("dashboard.noticias"))


# ==========================================================
# ADMINISTRAR ALIADOS
# ==========================================================

@dashboard_bp.route("/aliados")
@admin_required
def aliados():

    return render_template(
        "admin/aliados.html",
        aliados=ALIADOS
    )


# ==========================================================
# CREAR ALIADO
# ==========================================================

@dashboard_bp.route(
    "/aliados/nuevo",
    methods=["GET", "POST"]
)
@admin_required
def nuevo_aliado():

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        subtitulo = request.form.get("subtitulo", "").strip()
        icono = request.form.get("icono", "🌱").strip()
        descripcion = request.form.get("descripcion", "").strip()

        beneficios = []

        for i in range(1, 5):

            beneficio = request.form.get(
                f"beneficio_{i}",
                ""
            ).strip()

            if beneficio:
                beneficios.append(beneficio)

        if not nombre:

            flash(
                "El nombre del aliado es obligatorio.",
                "danger"
            )

            return redirect(
                url_for("dashboard.nuevo_aliado")
            )

        # Crear ID
        aliado_id = secure_filename(
            nombre.lower().replace(" ", "-")
        )

        # Evitar IDs repetidos
        id_original = aliado_id
        contador = 2

        while any(
            aliado["id"] == aliado_id
            for aliado in ALIADOS
        ):
            aliado_id = f"{id_original}-{contador}"
            contador += 1

        # Imagen predeterminada
        imagen = (
            "https://images.unsplash.com/"
            "photo-1574943320219-553eb213f72d"
            "?w=700&h=400&fit=crop&auto=format"
        )

        archivo = request.files.get("imagen")

        if archivo and archivo.filename:

            if not extension_permitida(archivo.filename):

                flash(
                    "Solo se permiten imágenes JPG, JPEG, PNG o WEBP.",
                    "danger"
                )

                return redirect(
                    url_for("dashboard.nuevo_aliado")
                )

            extension = (
                archivo.filename
                .rsplit(".", 1)[1]
                .lower()
            )

            marca_tiempo = int(time.time())

            nombre_archivo = secure_filename(
                f"aliado_{aliado_id}_{marca_tiempo}.{extension}"
            )

            carpeta_uploads = os.path.join(
                current_app.static_folder,
                "uploads"
            )

            os.makedirs(
                carpeta_uploads,
                exist_ok=True
            )

            archivo.save(
                os.path.join(
                    carpeta_uploads,
                    nombre_archivo
                )
            )

            imagen = (
                f"/static/uploads/{nombre_archivo}"
            )

        nuevo = {
            "id": aliado_id,
            "nombre": nombre,
            "subtitulo": subtitulo,
            "icono": icono,
            "imagen": imagen,
            "descripcion": descripcion,
            "beneficios": beneficios,
        }

        ALIADOS.append(nuevo)

        guardar_aliados()

        flash(
            "Aliado agregado correctamente.",
            "success"
        )

        return redirect(
            url_for("dashboard.aliados")
        )

    return render_template(
        "admin/form_aliado.html",
        aliado=None,
        titulo="Nuevo aliado"
    )


# ==========================================================
# EDITAR ALIADO
# ==========================================================

@dashboard_bp.route(
    "/aliados/<aliado_id>/editar",
    methods=["GET", "POST"]
)
@admin_required
def editar_aliado(aliado_id):

    aliado = next(
        (
            item
            for item in ALIADOS
            if item["id"] == aliado_id
        ),
        None
    )

    if not aliado:

        flash(
            "El aliado no existe.",
            "danger"
        )

        return redirect(
            url_for("dashboard.aliados")
        )

    if request.method == "POST":

        aliado["nombre"] = request.form.get(
            "nombre",
            ""
        ).strip()

        aliado["subtitulo"] = request.form.get(
            "subtitulo",
            ""
        ).strip()

        aliado["icono"] = request.form.get(
            "icono",
            ""
        ).strip()

        aliado["descripcion"] = request.form.get(
            "descripcion",
            ""
        ).strip()

        beneficios = []

        for i in range(1, 5):

            beneficio = request.form.get(
                f"beneficio_{i}",
                ""
            ).strip()

            if beneficio:
                beneficios.append(beneficio)

        aliado["beneficios"] = beneficios

        archivo = request.files.get("imagen")

        if archivo and archivo.filename:

            if not extension_permitida(archivo.filename):

                flash(
                    "Solo se permiten imágenes JPG, JPEG, PNG o WEBP.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "dashboard.editar_aliado",
                        aliado_id=aliado_id
                    )
                )

            extension = (
                archivo.filename
                .rsplit(".", 1)[1]
                .lower()
            )

            marca_tiempo = int(time.time())

            nombre_archivo = secure_filename(
                f"aliado_{aliado_id}_{marca_tiempo}.{extension}"
            )

            carpeta_uploads = os.path.join(
                current_app.static_folder,
                "uploads"
            )

            os.makedirs(
                carpeta_uploads,
                exist_ok=True
            )

            archivo.save(
                os.path.join(
                    carpeta_uploads,
                    nombre_archivo
                )
            )

            aliado["imagen"] = (
                f"/static/uploads/{nombre_archivo}"
            )

        guardar_aliados()

        flash(
            "Aliado actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("dashboard.aliados")
        )

    return render_template(
        "admin/form_aliado.html",
        aliado=aliado,
        titulo="Editar aliado"
    )


# ==========================================================
# ELIMINAR ALIADO
# ==========================================================

@dashboard_bp.route(
    "/aliados/<aliado_id>/eliminar",
    methods=["POST"]
)
@admin_required
def eliminar_aliado(aliado_id):

    aliado = next(
        (
            item
            for item in ALIADOS
            if item["id"] == aliado_id
        ),
        None
    )

    if not aliado:

        flash(
            "El aliado no existe.",
            "danger"
        )

        return redirect(
            url_for("dashboard.aliados")
        )

    ALIADOS.remove(aliado)

    guardar_aliados()

    flash(
        "Aliado eliminado correctamente.",
        "success"
    )

    return redirect(
        url_for("dashboard.aliados")
    )
