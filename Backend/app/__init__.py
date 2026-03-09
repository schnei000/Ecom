import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from .config import Config
from .extension import db, migrate, bcrypt, cors, jwt
from flasgger import Swagger

# Charger les variables d'environnement depuis .env
load_dotenv()
# Importation de tous les blueprints
from .routes.auth import auth_bp
from .routes.products import products_bp
from .routes.order import order_bp
from .routes.panier import panier_bp
from .routes.transaction import transaction_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # CORS Configuration - Restreindre les origins
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    cors_origins = [origin.strip() for origin in cors_origins]
    cors.init_app(app, resources={
        r"/api/*": {"origins": cors_origins},
        r"/auth/*": {"origins": cors_origins}
    })
    
    jwt.init_app(app)

    # Configuration de Flasgger (Swagger)
    app.config['SWAGGER'] = {
        'title': 'E-Commerce API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'Une API RESTful pour une application E-Commerce. Toutes les routes protégées nécessitent un token JWT.',
        'specs_route': '/apidocs/',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': "Token d'accès JWT. Entrez 'Bearer {token}'."
            }
        },
        'definitions': {
            'Product': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'stock': {'type': 'integer'},
                    'price': {'type': 'number', 'format': 'float'},
                    'category_id': {'type': 'integer'}
                }
            },
            'Category': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'description': {'type': 'string'}
                }
            },
            'Panier': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'product_id': {'type': 'integer'},
                    'quantity': {'type': 'integer'},
                    'created_at': {'type': 'string', 'format': 'date-time'}
                }
            },
            'Transaction': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'order_id': {'type': 'integer'},
                    'amount': {'type': 'number', 'format': 'float'},
                    'status': {'type': 'string'},
                    'ref_externe': {'type': 'string'}
                }
            }
        }
    }
    swagger = Swagger(app)

    # Enregistrement des Blueprints avec des préfixes d'URL
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)  # /api/products et /api/categories
    app.register_blueprint(panier_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(transaction_bp)

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