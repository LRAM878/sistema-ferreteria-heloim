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