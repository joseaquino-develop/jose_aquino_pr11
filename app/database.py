from flask_sqlalchemy import SQLAlchemy

# Instancia única de SQLAlchemy para todo el proyecto.
# Se conecta a la app real con db.init_app(app) dentro de create_app()
# (patrón "application factory"), así se evitan imports circulares.
db = SQLAlchemy()
