from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db
from models.models import Cliente
from forms import ClienteForm

clients_bp = Blueprint('clients', __name__, url_prefix='/clientes')

@clients_bp.route('/')
@login_required
def index():
    search_query = request.args.get('search', '')
    
    if search_query:
        # Usamos db.session.query() que es 100% seguro contra el error AttributeError
        clientes = db.session.query(Cliente).filter(
            (Cliente.dui.ilike(f'%{search_query}%')) | 
            (Cliente.nombre.ilike(f'%{search_query}%'))
        ).all()
    else:
        clientes = db.session.query(Cliente).all()
        
    return render_template('clientes/index.html', clientes=clientes, search_query=search_query)

@clients_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = ClienteForm()
    
    if form.validate_on_submit():
        # Verificamos si el DUI existe usando la sintaxis segura
        existe = db.session.query(Cliente).filter_by(dui=form.dui.data).first()
        
        if existe:
            flash('⚠️ Error: Este DUI ya está registrado en el sistema.', 'danger')
            return redirect(url_for('clients.nuevo'))

        # Creamos el cliente incluyendo la dirección
        nuevo_cliente = Cliente(
            dui=form.dui.data,
            nombre=form.nombre.data,
            telefono=form.telefono.data,
            correo=form.correo.data,
            direccion=form.direccion.data
        )
        
        db.session.add(nuevo_cliente)
        db.session.commit()
        flash('¡Cliente registrado exitosamente!', 'success')
        return redirect(url_for('clients.index'))
        
    return render_template('clientes/form.html', form=form, titulo="Registrar Nuevo Cliente")
@clients_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    # Buscamos al cliente por su ID
    cliente = db.session.query(Cliente).get_or_404(id)
    
    # Cargamos el formulario con los datos actuales del cliente
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        # Actualizamos los datos
        cliente.dui = form.dui.data
        cliente.nombre = form.nombre.data
        cliente.telefono = form.telefono.data
        cliente.correo = form.correo.data
        cliente.direccion = form.direccion.data
        
        db.session.commit()
        flash('¡Cliente actualizado exitosamente!', 'success')
        return redirect(url_for('clients.index'))
        
    return render_template('clientes/form.html', form=form, titulo="Editar Cliente")


@clients_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    cliente = db.session.query(Cliente).get_or_404(id)
    
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        # Si el cliente ya tiene una venta, la base de datos no dejará borrarlo por seguridad
        flash('⚠️ No se puede eliminar este cliente porque ya tiene ventas registradas en el sistema.', 'danger')
        
    return redirect(url_for('clients.index'))