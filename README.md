
# Chavalina

## Configuración de la base de datos

En desarrollo y producción la aplicación usa MySQL. Para el contenedor
MySQL local de Chavalina, configura estas variables en `.env`:

```text
DB_HOST=127.0.0.1
DB_PORT=3313
DB_NAME=chavalina_db
DB_USER=admin_chavalina
DB_PASSWORD=<contraseña del usuario MySQL>
```

La contraseña se lee del entorno y no se guarda en el código. El `.env` está
excluido de Git. Las pruebas usan SQLite en memoria y no requieren conectarse
a MySQL. Al iniciar, la aplicación crea las tablas que aún no existan; no
modifica ni migra datos de otras bases de datos.

Instala las dependencias y ejecuta la aplicación desde PowerShell:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe app.py
```

Para ejecutar la aplicación web dentro de Docker, el contenedor puede llegar a
MySQL en el equipo anfitrión mediante `host.docker.internal`:

```powershell
docker build -t chavalina-app .
docker run --rm --env-file .env -e DB_HOST=host.docker.internal -p 5000:5000 chavalina-app
```

Si existen datos en SQLite o Aiven, deben exportarse e importarse aparte; el
cambio de conexión no los transfiere automáticamente.

### Noticias

El panel administra noticias desde `/dashboard/noticias`. Las publicaciones
se guardan en la tabla MySQL `noticias`; la página pública consulta esa tabla
en cada visita a `/noticias`. Las imágenes nuevas se guardan en
`app/static/img/noticias/` y la base registra una ruta relativa a `static`.
Las rutas históricas con prefijo `static/` también se normalizan al mostrarse.
