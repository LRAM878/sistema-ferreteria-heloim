from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import extract
from models.models import db, Venta
from datetime import datetime

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

def solo_admin():
    if not hasattr(current_user, 'rol') or current_user.rol.lower() != 'administrador':
        flash('Acceso denegado: Solo los administradores pueden generar reportes.', 'danger')
        return False
    return True

@reportes_bp.route('/mensual')
@login_required
def mensual():
    if not solo_admin(): return redirect(url_for('dashboard.index'))

    # Obtenemos la fecha actual por defecto si el usuario aún no ha filtrado
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year

    # Capturamos los filtros del formulario
    mes = request.args.get('mes', default=mes_actual, type=int)
    anio = request.args.get('anio', default=anio_actual, type=int)

    # Buscamos las ventas que coincidan con ese mes y año
    ventas = Venta.query.filter(
        extract('month', Venta.fecha) == mes,
        extract('year', Venta.fecha) == anio
    ).order_by(Venta.fecha.desc()).all()

    # Calculamos el total de ingresos del mes
    total_mes = sum(v.total for v in ventas)

    return render_template('reportes/mensual.html', 
                           ventas=ventas, 
                           mes=mes, 
                           anio=anio,
                           total_mes=total_mes)