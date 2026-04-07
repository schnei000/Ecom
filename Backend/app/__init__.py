import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request, g
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import get_config, _validate_production_config
from .extension import db, migrate, bcrypt, cors, jwt, limiter
from .logging_config import setup_logging, log_security_event
from flasgger import Swagger

load_dotenv()

from .routes.auth import auth_bp
from .routes.users import users_bp
from .models import TokenBlocklist
from .routes.products import products_bp
from .routes.categories import categories_bp
from .routes.order import order_bp
from .routes.panier import panier_bp
from .routes.transaction import transaction_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    config = get_config()
    app.config.from_object(config)
    _validate_production_config()

    Path(app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    logger = setup_logging(app)
    app.logger = logger

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Hash factice pré-calculé pour prévenir les timing attacks sur le login
    # (bcrypt est toujours exécuté même si l'utilisateur n'existe pas)
    app.config['_TIMING_DUMMY_HASH'] = bcrypt.generate_password_hash('__timing_dummy__').decode('utf-8')

    # Support du reverse proxy (nginx, etc.) — désactivé par défaut
    if app.config.get('TRUST_PROXY_HEADERS'):
        hops = int(app.config.get('TRUST_PROXY_HOPS', 1))
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=hops, x_proto=hops, x_host=hops, x_port=hops, x_prefix=hops
        )

    import re
    cors_origins = []
    for origin in app.config['CORS_ORIGINS']:
        origin = origin.strip()
        if origin.startswith('r:'):
            cors_origins.append(re.compile(origin[2:]))
        else:
            cors_origins.append(origin)
    cors.init_app(app, resources={
        r"/api/v1/*": {"origins": cors_origins},
        r"/auth/v1/*": {"origins": cors_origins},
        r"/apidocs/*": {"origins": cors_origins}
    })

    jwt.init_app(app)
    limiter.init_app(app)

    # Blocklist JWT : vérifie si un token a été révoqué (logout/rotation)
    app.config["JWT_BLOCKLIST_ENABLED"] = True
    app.config["JWT_BLOCKLIST_TOKEN_CHECKS"] = ["access", "refresh"]

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        from datetime import datetime, timezone
        import random
        jti = jwt_payload.get("jti")
        if not jti:
            return False
        # Purge probabiliste (1/100) pour éviter la croissance infinie de la table
        if random.randint(1, 100) == 1:
            try:
                TokenBlocklist.purge_expired()
            except Exception:
                pass  # Ne jamais bloquer une requête pour une purge ratée
        return TokenBlocklist.query.filter_by(jti=jti).first() is not None

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
                    'category_id': {'type': 'integer'},
                    'image_url': {'type': 'string'}
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
            },
            'Order': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'total_amount': {'type': 'number', 'format': 'float'},
                    'status': {'type': 'string', 'enum': ['pending', 'paid', 'cancelled']},
                    'created_at': {'type': 'string', 'format': 'date-time'},
                    'updated_at': {'type': 'string', 'format': 'date-time'},
                    'items': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/OrderItem'}
                    }
                }
            },
            'OrderItem': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'order_id': {'type': 'integer'},
                    'product_id': {'type': 'integer'},
                    'quantity': {'type': 'integer'},
                    'unity_price': {'type': 'number', 'format': 'float'}
                }
            }
        }
    }
    swagger = Swagger(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(panier_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(transaction_bp)

    # En-têtes de sécurité OWASP sur toutes les réponses
    is_production = config.__name__ == 'ProductionConfig'

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        if is_production or os.environ.get('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    @app.before_request
    def log_request():
        g.start_time = app.logger.info(
            f"Request: {request.method} {request.path} from {request.remote_addr}"
        )

    @app.after_request
    def log_response(response):
        app.logger.info(
            f"Response: {request.method} {request.path} -> {response.status_code}"
        )
        return response

    @app.route('/', methods=['GET'])
    def home():
        endpoints_dict = {}
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                url = str(rule)
                methods = sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
                endpoints_dict[url] = {'methods': methods, 'endpoint': rule.endpoint}
        return jsonify({
            'message': "Bienvenue à l'API E-Commerce",
            'total_endpoints': len(endpoints_dict),
            'endpoints': endpoints_dict
        })

    # Gestionnaires d'erreurs globaux
    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f"Bad request: {error}")
        return jsonify({"success": False, "message": "Requête invalide."}), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        app.logger.warning(f"Unauthorized access attempt: {request.path} from {request.remote_addr}")
        return jsonify({"success": False, "message": "Authentification requise."}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"Forbidden access attempt: {request.path} from {request.remote_addr}")
        return jsonify({"success": False, "message": "Accès refusé."}), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"success": False, "message": "Ressource non trouvée."}), 404

    @app.errorhandler(429)
    def rate_limit_error(error):
        app.logger.warning(f"Rate limit exceeded: {request.path} from {request.remote_addr}")
        return jsonify({"success": False, "message": "Trop de requêtes. Veuillez réessayer plus tard."}), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur interne du serveur."}), 500

    @app.errorhandler(503)
    def service_unavailable_error(error):
        app.logger.error(f"Service unavailable: {error}")
        return jsonify({"success": False, "message": "Service indisponible. Veuillez réessayer plus tard."}), 503

    app.logger.info(f"Flask app created with config: {config.__name__}")
    return app
