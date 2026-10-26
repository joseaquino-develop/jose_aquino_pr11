from app.database import db


class Cotizacion(db.Model):
    """Solicitud de cotización comercial (B2B) enviada desde la web pública
    o registrada manualmente desde el panel administrativo.

    Esta tabla guarda las solicitudes de cotización de agroexportadoras,
    importadores, mercados mayoristas, etc.
    """

    __tablename__ = "quotations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Paso 1: datos de la empresa
    empresa = db.Column("company", db.String(255), nullable=False)
    contacto = db.Column("contact_name", db.String(255), nullable=False)
    cargo = db.Column("contact_position", db.String(100), nullable=True)
    pais = db.Column("country", db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    telefono = db.Column("phone", db.String(50), nullable=True)
    web = db.Column("website", db.String(255), nullable=True)

    # Paso 2: producto y volumen
    producto = db.Column("product", db.String(100), nullable=False)
    cantidad = db.Column("quantity", db.String(50), nullable=False)
    unidad = db.Column("unit", db.String(50), nullable=True)
    frecuencia = db.Column("frequency", db.String(100), nullable=True)
    destino = db.Column("destination", db.String(150), nullable=True)

    # Paso 3: requisitos técnicos
    incoterm = db.Column(db.String(50), nullable=True)
    certificaciones = db.Column("certifications", db.String(255), nullable=True)
    notas = db.Column("notes", db.Text, nullable=True)

    creado_en = db.Column("request_date", db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Cotizacion {self.id} {self.empresa}>"