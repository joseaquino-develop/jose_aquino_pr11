import os
from sqlalchemy.engine import URL


def database_config(env):
    if env == "testing":
        return {"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}

    password = os.environ.get("DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "Falta DB_PASSWORD en el entorno para conectar con MySQL."
        )

    uri = URL.create(
        drivername="mysql+pymysql",
        username=os.environ.get("DB_USER", "chavalina"),
        password=password,
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", "3314")),
        database=os.environ.get("DB_NAME", "chavalina_db"),
    )
    return {"SQLALCHEMY_DATABASE_URI": uri}


class Config:
    """Configuración base, común a todos los entornos."""
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "cambia-esta-clave-en-produccion"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
