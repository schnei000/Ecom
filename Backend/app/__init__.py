from flask import Flask
from config import Config
from extension import db, migrate, bcrypt, cors, jwt
from routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init= app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    #enrefistrement des Blueprints
    app.register_blueprint(auth_bp)

    return app