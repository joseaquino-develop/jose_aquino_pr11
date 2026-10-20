from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services import cotizacion_service


# CRUD antiguo de cotizaciones.
# Se mantiene separado del nuevo panel administrativo
# para evitar conflictos con /admin/cotizaciones.
cotizaciones_bp = Blueprint(
    "cotizaciones",
    __name__,
    url_prefix="/gestion-cotizaciones"
)


@cotizaciones_bp.route("/")
def index():
    cotizaciones = cotizacion_service.obtener_cotizaciones()

    return render_template(
        "cotizaciones/index.html",
        cotizaciones=cotizaciones
    )


@cotizaciones_bp.route("/nueva", methods=["GET", "POST"])
def nueva():

    if request.method == "POST":

        cotizacion_service.crear_cotizacion(request.form)

        flash(
            "Cotización registrada correctamente.",
            "success"
        )

        return redirect(
            url_for("cotizaciones.index")
        )

    return render_template(
        "cotizaciones/form.html",
        cotizacion=None
    )


@cotizaciones_bp.route(
    "/<int:cotizacion_id>/editar",
    methods=["GET", "POST"]
)
def editar(cotizacion_id):

    cotizacion = cotizacion_service.obtener_cotizacion(
        cotizacion_id
    )

    if request.method == "POST":

        cotizacion_service.actualizar_cotizacion(
            cotizacion_id,
            request.form
        )

        flash(
            "Cotización actualizada correctamente.",
            "success"
        )

        return redirect(
            url_for("cotizaciones.index")
        )

    return render_template(
        "cotizaciones/form.html",
        cotizacion=cotizacion
    )


@cotizaciones_bp.route(
    "/<int:cotizacion_id>/eliminar",
    methods=["POST"]
)
def eliminar(cotizacion_id):

    cotizacion_service.eliminar_cotizacion(
        cotizacion_id
    )

    flash(
        "Cotización eliminada.",
        "info"
    )

    return redirect(
        url_for("cotizaciones.index")
    )