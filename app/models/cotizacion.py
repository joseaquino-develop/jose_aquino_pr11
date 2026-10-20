from app.database import db


class Cotizacion(db.Model):
    """Solicitud de cotización comercial (B2B) enviada desde la web pública
    o registrada manualmente desde el panel administrativo.

    Esta tabla guarda las solicitudes de cotización de agroexportadoras,
    importadores, mercados mayoristas, etc.
    """

    __tablename__ = "cotizaciones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Paso 1: datos de la empresa
    empresa = db.Column(db.String(150), nullable=False)
    contacto = db.Column(db.String(120), nullable=False)
    cargo = db.Column(db.String(120), nullable=True)
    pais = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(50), nullable=False)  # Coincide con VARCHAR(50) de la BD
    web = db.Column(db.String(150), nullable=True)

    # Paso 2: producto y volumen
    producto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.String(100), nullable=False)
    unidad = db.Column(db.String(50), nullable=True)
    frecuencia = db.Column(db.String(50), nullable=True)
    destino = db.Column(db.String(150), nullable=True)

    # Paso 3: requisitos técnicos
    incoterm = db.Column(db.String(50), nullable=True)
    certificaciones = db.Column(db.Text, nullable=True)  # ej: "SENASA, GlobalG.A.P."
    notas = db.Column(db.Text, nullable=True)

    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Cotizacion {self.id} {self.empresa}>"