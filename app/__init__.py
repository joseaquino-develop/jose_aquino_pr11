import os

from flask import Flask

from app.config import config_by_name, database_config
from app.database import db


def normalizar_ruta_imagen(valor):
    fallback = "/static/img/logo-chavalina.png"
    if not valor:
        return fallback

    v = str(valor).strip()
    if not v:
        return fallback

    lower = v.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        return v

    if v.startswith("/static/"):
        return v

    if v.startswith("static/"):
        return f"/{v}"

    if ":" in v or v.startswith("\\\\"):
        return fallback

    if "/" not in v and "\\" not in v:
        return f"/static/uploads/{v}"

    return fallback


def create_app(env=None):
    """Factory function: crea, configura y devuelve la aplicación Flask."""

    env = env or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[env])

    app.config.update(database_config(env))

    app.jinja_env.filters["normalizar_ruta_imagen"] = normalizar_ruta_imagen


    # Clave necesaria para utilizar sesiones
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.environ.get(
            "SECRET_KEY",
            "chavalina-desarrollo-2026"
        )

    # Extensiones
    db.init_app(app)

    # Blueprints
    from app.routes.authentication import authentication_bp
    from app.routes.cotizaciones import cotizaciones_bp
    from app.routes.public import public_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(authentication_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(cotizaciones_bp)
    app.register_blueprint(dashboard_bp)

    with app.app_context():

        # Importar modelos para reconocer las tablas
        from app.models import (
            Maestro,
            Estudiante,
            Entrenamiento,
            Inscripcion,
            Pago
        )

        # Crear las tablas que falten sin modificar las existentes.
        db.create_all()

    return app