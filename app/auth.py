from functools import wraps

from flask import flash, redirect, session, url_for


def admin_required(func):
    @wraps(func)
    def funcion_protegida(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Acceso restringido solo para administradores", "error")
            return redirect(url_for("authentication.admin_login"))

        return func(*args, **kwargs)

    return funcion_protegida
