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