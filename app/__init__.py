import os

from flask import Flask

from app.config import config_by_name
from app.database import db


def create_app(env=None):
    """Factory function: crea, configura y devuelve la aplicación Flask."""

    env = env or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[env])

    # Clave necesaria para utilizar sesiones
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.environ.get(
            "SECRET_KEY",
            "chavalina-desarrollo-2026"
        )

    # Extensiones
    db.init_app(app)

    # Blueprints
    from app.routes.cotizaciones import cotizaciones_bp
    from app.routes.public import public_bp
    from app.routes.dashboard import dashboard_bp

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

        db.create_all()

    return app