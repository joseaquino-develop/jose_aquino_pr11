from datetime import datetime
from app.database import db
from .cotizacion import Cotizacion
from .contactos import Contacto
from .noticia import Noticia
from .user import User


class Maestro(db.Model):
    __tablename__ = "maestros"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    correo = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    entrenamientos = db.relationship("Entrenamiento", backref="maestro", lazy=True)


class Estudiante(db.Model):
    __tablename__ = "estudiantes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    nivel_voley = db.Column(db.String(50))
    correo = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    estado = db.Column(db.String(20), default="Activo")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    inscripciones = db.relationship("Inscripcion", backref="estudiante", lazy=True)
    pagos = db.relationship("Pago", backref="estudiante", lazy=True)


class Entrenamiento(db.Model):
    __tablename__ = "entrenamientos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    maestro_id = db.Column(
        db.Integer, db.ForeignKey("maestros.id", ondelete="SET NULL")
    )
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    horario = db.Column(db.DateTime, nullable=False)
    cupos = db.Column(db.Integer, nullable=False)
    nivel = db.Column(db.String(50))
    inscripciones = db.relationship(
        "Inscripcion", backref="entrenamiento", lazy=True
    )


class Inscripcion(db.Model):
    __tablename__ = "inscripciones"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudiante_id = db.Column(
        db.Integer, db.ForeignKey("estudiantes.id", ondelete="CASCADE")
    )
    entrenamiento_id = db.Column(
        db.Integer, db.ForeignKey("entrenamientos.id", ondelete="CASCADE")
    )
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    estado_pago = db.Column(db.String(30), default="Pendiente")


class Pago(db.Model):
    __tablename__ = "pagos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudiante_id = db.Column(
        db.Integer, db.ForeignKey("estudiantes.id", ondelete="CASCADE")
    )
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(50))
    estado = db.Column(db.String(30), default="Completado")
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)