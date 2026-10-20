import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Abre una conexión a MySQL con los datos del archivo .env"""
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
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