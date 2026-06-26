from flask import Blueprint, render_template
from flask_login import login_required
from models.models import Producto, MovimientoInventario

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # 1. Contar total de productos en el catálogo
    total_productos = Producto.query.count()
    
    # 2. Buscar productos que necesitan reabastecimiento (stock <= stock mínimo)
    productos_bajos = Producto.query.filter(Producto.stock_actual <= Producto.stock_minimo).all()
    alertas_stock = len(productos_bajos)
    
    # 3. Traer los últimos 5 movimientos (ventas o salidas)
    ultimos_movimientos = MovimientoInventario.query.order_by(MovimientoInventario.fecha.desc()).limit(5).all()

    return render_template('dashboard/index.html', 
                           total_productos=total_productos, 
                           alertas_stock=alertas_stock,
                           productos_bajos=productos_bajos,
                           ultimos_movimientos=ultimos_movimientos)