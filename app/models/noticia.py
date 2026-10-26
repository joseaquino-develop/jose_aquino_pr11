from pathlib import Path

from flask import current_app

from app.database import db


class Noticia(db.Model):
    __tablename__ = "noticias"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoria = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    resumen = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)

    @property
    def _static_root(self):
        return Path(current_app.static_folder).resolve()

    @property
    def _imagen_relativa(self):
        if not self.imagen or self.imagen.startswith(("http://", "https://")):
            return None

        filename = self.imagen.replace("\\", "/").lstrip("/")
        if filename.startswith("static/"):
            filename = filename[len("static/"):]

        image_root = self._static_root
        image_path = (image_root / filename).resolve()
        try:
            return image_path.relative_to(image_root).as_posix()
        except ValueError:
            return None

    @property
    def imagen_disponible(self):
        if not self.imagen:
            return False
        if self.imagen.startswith(("http://", "https://")):
            return True

        filename = self._imagen_relativa
        if not filename:
            return False

        return (self._static_root / filename).is_file()

    @property
    def imagen_url(self):
        if not self.imagen:
            return ""
        if self.imagen.startswith(("http://", "https://")):
            return self.imagen

        filename = self._imagen_relativa
        if not filename or not self.imagen_disponible:
            return "/static/img/noticia-placeholder.svg"

        modified = (self._static_root / filename).stat().st_mtime_ns
        return f"/static/{filename}?v={modified}"
