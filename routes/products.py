from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.models import Producto, Categoria, Proveedor
from forms import ProductoForm

products_bp = Blueprint('products', __name__, url_prefix='/productos')

@products_bp.route('/')
@login_required
def index():
    
    if current_user.rol != 'Administrador':
        flash('Acceso denegado: Solo los administradores pueden ver el inventario.', 'danger')
        return redirect(url_for('dashboard.index'))
    #  CAPTURAMOS LA BÚSQUEDA: Buscamos si el usuario envió texto en la barra
    search_query = request.args.get('search', '')
    
    if search_query:
        # Filtramos por código O por nombre ignorando mayúsculas (ilike)
        productos = Producto.query.filter(
            (Producto.codigo.ilike(f'%{search_query}%')) | 
            (Producto.nombre.ilike(f'%{search_query}%'))
        ).all()
    else:
        # Si no hay búsqueda, mostramos todo
        productos = Producto.query.all()
        
    return render_template('productos/index.html', productos=productos, search_query=search_query)

@products_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if Categoria.query.count() == 0:
        cat_defecto = Categoria(nombre="General", descripcion="Categoría por defecto")
        db.session.add(cat_defecto)
        db.session.commit()

    form = ProductoForm()
    form.categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.all()]
    
    # NUEVO: Obtenemos los proveedores para mandarlos al HTML
    proveedores = Proveedor.query.all()
    
    if form.validate_on_submit():
        #  SEGURO ANTI-DUPLICADOS: Verificamos si el código/ID ya existe en la BD
        existe = Producto.query.filter_by(codigo=form.codigo.data).first()
        if existe:
            flash('⚠️ Error: Este ID o Código ya está ocupado. Por favor, usa uno diferente.', 'danger')
            return redirect(url_for('products.nuevo'))

        # NUEVO: Capturamos el proveedor seleccionado (si lo dejaron vacío, mandamos None)
        prov_id = request.form.get('proveedor_id')
        if not prov_id:
            prov_id = None

        nuevo_prod = Producto(
            codigo=form.codigo.data,
            nombre=form.nombre.data,
            categoria_id=form.categoria_id.data,
            proveedor_id=prov_id,  # <-- Asignamos el proveedor
            precio_compra=form.precio_compra.data,
            precio_venta=form.precio_venta.data,
            stock_actual=form.stock_actual.data,
            stock_minimo=form.stock_minimo.data
        )
        db.session.add(nuevo_prod)
        db.session.commit()
        flash('¡Producto registrado exitosamente!', 'success')
        return redirect(url_for('products.index'))
        
    return render_template('productos/form.html', form=form, titulo="Registrar Nuevo Producto", proveedores=proveedores, producto=None)

@products_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    form.categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.all()]
    
    # NUEVO: Obtenemos los proveedores
    proveedores = Proveedor.query.all()

    if form.validate_on_submit():
        # 🛡️ SEGURO ANTI-DUPLICADOS
        existe = Producto.query.filter_by(codigo=form.codigo.data).first()
        if existe and existe.id != id:
            flash('⚠️ Error: Este ID o Código ya está ocupado por otro producto distinto.', 'danger')
            return redirect(url_for('products.editar', id=id))
        
        # NUEVO: Capturamos y actualizamos el proveedor
        prov_id = request.form.get('proveedor_id')
        
        producto.codigo = form.codigo.data
        producto.nombre = form.nombre.data
        producto.categoria_id = form.categoria_id.data
        producto.proveedor_id = prov_id if prov_id else None # <-- Actualizamos el proveedor
        producto.precio_compra = form.precio_compra.data
        producto.precio_venta = form.precio_venta.data
        producto.stock_actual = form.stock_actual.data
        producto.stock_minimo = form.stock_minimo.data
        
        db.session.commit()
        flash('¡Producto actualizado correctamente!', 'success')
        return redirect(url_for('products.index'))

    return render_template('productos/form.html', form=form, titulo=" Editar Producto", proveedores=proveedores, producto=producto)

@products_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado del sistema de forma permanente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar el producto porque ya tiene movimientos en el registro de ventas.', 'danger')
        
    return redirect(url_for('products.index'))