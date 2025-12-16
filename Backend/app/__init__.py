from flask import Flask, jsonify
from .config import Config
from .extension import db, migrate, bcrypt, cors, jwt
# Importation de tous les blueprints
from .routes.auth import auth_bp
from .routes.order import order_bp
from .routes.panier import panier_bp
from .routes.transaction import transaction_bp
from .admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    # Enregistrement des Blueprints avec des préfixes d'URL
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(panier_bp, url_prefix='/api')
    app.register_blueprint(order_bp, url_prefix='/api')
    app.register_blueprint(transaction_bp, url_prefix='/api')
    app.register_blueprint(admin_bp) # Le préfixe '/admin' est déjà dans sa définition

    # Route d'accueil affichant tous les endpoints
    @app.route('/', methods=['GET'])
    def home():
        """Route d'accueil listant tous les endpoints disponibles"""
        endpoints_dict = {}
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                url = str(rule)
                methods = sorted([method for method in rule.methods if method not in ['HEAD', 'OPTIONS']])
                endpoints_dict[url] = {
                    'methods': methods,
                    'endpoint': rule.endpoint
                }
        
        return jsonify({
            'message': 'Bienvenue à l\'API E-Commerce',
            'total_endpoints': len(endpoints_dict),
            'endpoints': endpoints_dict
        })

    return app