from flask import Flask, render_template, redirect, url_for
from config import Config
from models import db
from models.models import Usuario
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints (Rutas)
    from routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    from routes.sales import sales_bp
    app.register_blueprint(sales_bp)
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    from routes.products import products_bp
    app.register_blueprint(products_bp)
    from routes.clients import clients_bp
    app.register_blueprint(clients_bp)
    from routes.proveedores import proveedores_bp
    app.register_blueprint(proveedores_bp)
    from routes.reportes import reportes_bp
    app.register_blueprint(reportes_bp)
    from werkzeug.security import generate_password_hash
    from models.models import Usuario 

    with app.app_context():
        db.create_all() # Crea las tablas si no existen
        
        # Lista de usuarios a crear
        usuarios_default = [
            {'username': 'admin', 'password': 'admin123', 'rol': 'Administrador'},
            {'username': 'vendedor', 'password': 'vendedor123', 'rol': 'Vendedor'}
        ]
        
        for u in usuarios_default:
            existe = Usuario.query.filter_by(username=u['username']).first()
            if not existe:
                nuevo_usuario = Usuario(
                    username=u['username'],
                    password_hash=generate_password_hash(u['password']),
                    rol=u['rol'],
                    estado=True
                )
                db.session.add(nuevo_usuario)
        
        db.session.commit()

    @app.route('/')
    def home():
        return redirect(url_for('dashboard.index'))
    @app.route('/setup-categorias')
    def setup_categorias():
        from models.models import Categoria
        from models import db
        
        categorias_fijas = [
            'Construcción', 'Fontanería', 'Electricidad', 
            'Pinturas', 'Automotriz', 'Herramientas', 'Carpintería'
        ]
        
        for cat_nombre in categorias_fijas:
            # Verifica si la categoría ya existe para no duplicarla
            existe = Categoria.query.filter_by(nombre=cat_nombre).first()
            if not existe:
                nueva_cat = Categoria(nombre=cat_nombre, descripcion=f"Área de {cat_nombre}")
                db.session.add(nueva_cat)
                
        db.session.commit()
        return "¡Categorías creadas con éxito! Ya puedes regresar al sistema."


    return app 


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)