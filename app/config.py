
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv(override=True)


def _database_url():
    """Construye la URL de conexión a MySQL."""

    database_settings = (
        "DB_HOST",
        "DB_PORT",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    )

    # Usar las variables DB_* si están definidas.
    if all(os.getenv(key) is not None for key in database_settings):
        user = quote_plus(os.getenv("DB_USER"))
        password = quote_plus(os.getenv("DB_PASSWORD"))
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")

        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{host}:{port}/{database}?charset=utf8mb4"
        )

    # Si no están todas las variables DB_*, usar DATABASE_URL.
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # Valores predeterminados para desarrollo local.
    user = quote_plus(os.getenv("DB_USER", "chavalina_app"))
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "chavalina_db")

    return (
        f"mysql+pymysql://{user}:{password}"
        f"@{host}:{port}/{database}?charset=utf8mb4"
    )


class Config:
    """Configuración base de Flask."""

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "clave-local-desarrollo",
    )

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Configuración de desarrollo."""

    DEBUG = True


class TestingConfig(Config):
    """Configuración para pruebas."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:",
    )


class ProductionConfig(Config):
    """Configuración de producción."""

    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
