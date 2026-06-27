from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, Proveedor

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

def solo_admin():
    if not hasattr(current_user, 'rol') or current_user.rol.lower() != 'administrador':
        flash('Acceso denegado: Solo los administradores pueden gestionar proveedores.', 'danger')
        return False
    return True

@proveedores_bp.route('/')
@login_required
def index():
    if not solo_admin(): return redirect(url_for('dashboard.index'))
    proveedores = Proveedor.query.all()
    return render_template('proveedores/index.html', proveedores=proveedores)

@proveedores_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if not solo_admin(): return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        direccion = request.form.get('direccion')
        
        nuevo_prov = Proveedor(nombre=nombre, telefono=telefono, correo=correo, direccion=direccion)
        db.session.add(nuevo_prov)
        db.session.commit()
        flash('¡Proveedor registrado exitosamente!', 'success')
        return redirect(url_for('proveedores.index'))
        
    return render_template('proveedores/nuevo.html') # <-- Muestra la nueva pantalla


# ==========================================
# NUEVAS RUTAS AGREGADAS (EDITAR Y ELIMINAR)
# ==========================================

@proveedores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not solo_admin(): return redirect(url_for('dashboard.index'))
    
    # Buscamos el proveedor por su ID
    proveedor = Proveedor.query.get_or_404(id)
    
    if request.method == 'POST':
        # Actualizamos los datos con lo que viene del formulario
        proveedor.nombre = request.form.get('nombre')
        proveedor.telefono = request.form.get('telefono')
        proveedor.correo = request.form.get('correo')
        proveedor.direccion = request.form.get('direccion')
        
        db.session.commit()
        flash('¡Proveedor actualizado exitosamente!', 'success')
        return redirect(url_for('proveedores.index'))
        
    # Renderizamos la plantilla para editar, pasándole los datos del proveedor actual
    return render_template('proveedores/editar.html', proveedor=proveedor)


@proveedores_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    if not solo_admin(): return redirect(url_for('dashboard.index'))
    
    proveedor = Proveedor.query.get_or_404(id)
    
    try:
        db.session.delete(proveedor)
        db.session.commit()
        flash('¡Proveedor eliminado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        # Esto previene errores 500 si intentas borrar un proveedor que ya está amarrado a un producto
        flash('Error: No se puede eliminar este proveedor porque ya está asignado a uno o más productos.', 'danger')
        
    return redirect(url_for('proveedores.index'))