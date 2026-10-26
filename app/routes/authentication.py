from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash

from app.database import db
from app.models.user import User


authentication_bp = Blueprint("authentication", __name__)


def _clean(value):
    if value is None:
        return None
    value = value.strip()
    return value or None


@authentication_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = _clean(request.form.get("username"))
        password = request.form.get("password", "")

        try:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                if user.role == "admin":
                    session.clear()
                    session["username"] = user.username
                    session["name"] = user.name
                    session["role"] = user.role
                    return redirect(url_for("dashboard.index"))

            return render_template(
                "admin/login.html",
                error="Usuario o contraseña incorrectos o tipo de cuenta no permitido.",
            )
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception(
                "Error en base de datos al iniciar sesión"
            )
            return render_template(
                "admin/login.html",
                error="Error de conexión con la base de datos.",
            )

    return render_template("admin/login.html")


@authentication_bp.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return redirect(url_for("authentication.admin_login"))
