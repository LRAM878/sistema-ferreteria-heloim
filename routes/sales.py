from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models.models import db, Venta, DetalleVenta, Producto, Cliente, MovimientoInventario

sales_bp = Blueprint('sales', __name__, url_prefix='/ventas')

@sales_bp.route('/nueva')
@login_required
def nueva():
   
    productos = db.session.query(Producto).filter(Producto.estado == True, Producto.stock_actual > 0).all()
    
    # CORRECCIÓN AQUÍ: Quitamos el filtro de estado porque la tabla Cliente no lo usa
    clientes = db.session.query(Cliente).all() 
    
    return render_template('ventas/nueva.html', productos=productos, clientes=clientes)


@sales_bp.route('/procesar', methods=['POST'])
@login_required
def procesar_venta():
    datos = request.get_json()
    carrito = datos.get('carrito', [])
    
    # CORRECCIÓN: Volvemos a usar cliente_id (como está en tu models.py)
    cliente_id = datos.get('cliente_id')
    if cliente_id == "" or cliente_id == "null" or cliente_id is None:
        cliente_id = None 

    # 👇 NUEVO: Capturamos el método de pago desde el frontend
    metodo_pago = datos.get('metodo_pago', 'Efectivo')

    if not carrito:
        return jsonify({'error': 'El carrito está vacío'}), 400

    try:
        total_venta = datos.get('total', 0)
        
        if not total_venta:
            for item in carrito:
                prod = db.session.query(Producto).get(item['producto_id'])
                if prod:
                    precio = getattr(prod, 'precio', getattr(prod, 'precio_venta', 0))
                    total_venta += float(precio) * int(item['cantidad'])

        # Creamos la Venta usando cliente_id y registrando el método de pago
        nueva_venta = Venta(
            total=total_venta,
            cliente_id=cliente_id,
            metodo_pago=metodo_pago  # 👈 NUEVO: Guardamos cómo pagó el cliente
        )
        db.session.add(nueva_venta)
        db.session.flush() 

        for item in carrito:
            producto = db.session.query(Producto).get(item['producto_id'])
            
            if not producto or producto.stock_actual < item['cantidad']:
                db.session.rollback()
                return jsonify({'error': f"Stock insuficiente para el producto ID {item['producto_id']}"}), 400

            # Descontar stock
            producto.stock_actual -= item['cantidad']

            # MANTENEMOS LA SOLUCIÓN DEL SUBTOTAL
            precio_unitario = getattr(producto, 'precio', getattr(producto, 'precio_venta', 0))
            subtotal_item = float(precio_unitario) * int(item['cantidad'])

            # Guardamos el detalle
            detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=producto.id,
                cantidad=item['cantidad'],
                precio_unitario=precio_unitario,
                subtotal=subtotal_item  
            )
            db.session.add(detalle)

            # Registrar en el historial de movimientos
            movimiento = MovimientoInventario(
                producto_id=producto.id,
                tipo='SALIDA',
                cantidad=item['cantidad'],
                motivo=f"Venta en caja #" + str(nueva_venta.id) + f" (Usuario: {current_user.username})"
            )
            db.session.add(movimiento)

        db.session.commit()
        return jsonify({'mensaje': 'Venta procesada con éxito'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@sales_bp.route('/historial')
@login_required  
def historial():
    # Obtenemos todas las ventas ordenadas por fecha descendente (las más nuevas primero)
    ventas = db.session.query(Venta).order_by(Venta.fecha.desc()).all()
    
    return render_template('ventas/historial.html', ventas=ventas)