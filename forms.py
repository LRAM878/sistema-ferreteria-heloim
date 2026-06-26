from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange, Optional, Email
from wtforms import StringField, PasswordField, SubmitField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

# --- NUEVO: Formulario de Productos ---
class ProductoForm(FlaskForm):
    codigo = StringField('Código de Barra / Único', validators=[DataRequired()])
    nombre = StringField('Nombre del Producto', validators=[DataRequired()])
    categoria_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    precio_compra = DecimalField('Precio de Compra ($)', validators=[DataRequired(), NumberRange(min=0)])
    precio_venta = DecimalField('Precio de Venta ($)', validators=[DataRequired(), NumberRange(min=0)])
    stock_actual = IntegerField('Stock Inicial', default=0, validators=[NumberRange(min=0)])
    stock_minimo = IntegerField('Stock Mínimo Alerta', default=5, validators=[NumberRange(min=0)])
    submit = SubmitField('Guardar Producto')

class ClienteForm(FlaskForm):
    dui = StringField('DUI (Ej: 12345678-9)', validators=[DataRequired()])
    nombre = StringField('Nombre Completo', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[Optional()])
    correo = StringField('Correo Electrónico', validators=[Optional(), Email(message="Dirección de correo no válida")])
    direccion = StringField('Dirección', validators=[Optional()]) # <-- Nuevo campo
    submit = SubmitField('Guardar Cliente')