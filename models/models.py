from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('Administrador', 'Vendedor'), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    rol = db.Column(db.String(20), nullable=False, default='admin')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)

    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)

    precio_compra = db.Column(db.Numeric(10, 2), nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    estado = db.Column(db.Boolean, default=True)

    
    # Relación para historial
    categoria = db.relationship('Categoria', backref='productos')
    movimientos = db.relationship('MovimientoInventario', backref='producto', lazy=True)

class MovimientoInventario(db.Model):
    __tablename__ = 'movimientos_inventario'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.Enum('ENTRADA', 'SALIDA'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class Cliente(db.Model):  # <-- ¡Ese (db.Model) es vital!
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    dui = db.Column(db.String(10), nullable=False, unique=True)
    
    ventas = db.relationship('Venta', backref='cliente', lazy=True)
    
    # Relación con ventas
    ventas = db.relationship('Venta', backref='cliente', lazy=True)
    
class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    # Nota: Si no tienes importado datetime en models.py, asegúrate de tenerlo
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp()) 
    total = db.Column(db.Numeric(10, 2), nullable=False)
    
    metodo_pago = db.Column(db.String(50), nullable=False, default='Efectivo')
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True)

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_ventas'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relación para acceder al nombre del producto fácilmente
    producto = db.relationship('Producto', backref='detalles_venta', lazy=True)
    
class Proveedor(db.Model):
    __tablename__ = 'proveedores' # Asegúrate de que este sea el nombre exacto de tu tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    
    # Relación con productos
    productos = db.relationship('Producto', backref='proveedor', lazy=True)
    