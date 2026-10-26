import os
import pymysql
from dotenv import load_dotenv

load_dotenv(override=True)


def get_connection():
    """Abre una conexión a MySQL con los datos del archivo .env"""
    required_settings = ("DB_NAME", "DB_USER", "DB_PASSWORD")
    missing_settings = [
        setting for setting in required_settings if os.getenv(setting) is None
    ]
    if missing_settings:
        raise RuntimeError(
            "Faltan variables de conexión MySQL: "
            + ", ".join(missing_settings)
        )

    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def guardar_mensaje(nombre, correo, asunto, mensaje, ip=None):
    """Inserta un mensaje del formulario de contacto."""
    sql = """
        INSERT INTO mensajes_contacto (nombre, correo, asunto, mensaje, ip_origen)
        VALUES (%s, %s, %s, %s, %s)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nombre, correo, asunto or None, mensaje, ip))
        conn.commit()
    finally:
        conn.close()


def obtener_aliados():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nombre, subtitulo, descripcion, imagen
                FROM aliados
                ORDER BY id ASC
                """
            )
            filas = cur.fetchall() or []
            return filas
    finally:
        conn.close()


def obtener_noticias():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, categoria, fecha, titulo, resumen, imagen
                FROM noticias
                ORDER BY id DESC
                """
            )
            filas = cur.fetchall() or []
            return filas
    finally:
        conn.close()