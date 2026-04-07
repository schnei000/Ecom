"""
Flask configuration module.
Supports multiple environments: development, testing, production.
"""

import os
from datetime import timedelta
from pathlib import Path


def _get_int_env(name: str, default: int) -> int:
    """Read integer environment variables with a safe fallback."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _get_bool_env(name: str, default: bool) -> bool:
    """Read boolean environment variables with a safe fallback."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_SECRET_KEY = 'dev-secret-key-change-in-production'
DEFAULT_JWT_ACCESS_EXPIRES = 3600
DEFAULT_JWT_REFRESH_EXPIRES = 2592000
MIN_PASSWORD_LENGTH = 8
BASE_DIR = Path(__file__).resolve().parents[1]

PASSWORD_REQUIREMENTS = {
    'min_length': MIN_PASSWORD_LENGTH,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digit': True,
    'require_special': True
}


class Config:
    """Base configuration class with common settings."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=_get_int_env('JWT_ACCESS_TOKEN_EXPIRES', DEFAULT_JWT_ACCESS_EXPIRES)
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=_get_int_env('JWT_REFRESH_TOKEN_EXPIRES', DEFAULT_JWT_REFRESH_EXPIRES)
    )
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    
    # Session security
    SESSION_COOKIE_SECURE = _get_bool_env('SESSION_COOKIE_SECURE', False)
    SESSION_COOKIE_HTTPONLY = _get_bool_env('SESSION_COOKIE_HTTPONLY', True)
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Password requirements
    PASSWORD_MIN_LENGTH = MIN_PASSWORD_LENGTH

    # Email confirmation enforcement
    EMAIL_CONFIRMATION_REQUIRED = _get_bool_env('EMAIL_CONFIRMATION_REQUIRED', False)

    # Pagination safety
    MAX_PER_PAGE = _get_int_env('MAX_PER_PAGE', 100)

    # Uploads
    MAX_CONTENT_LENGTH = _get_int_env('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)
    PRODUCT_IMAGE_MAX_BYTES = _get_int_env('PRODUCT_IMAGE_MAX_BYTES', 5 * 1024 * 1024)
    PRODUCT_IMAGE_UPLOAD_FOLDER = os.environ.get(
        'PRODUCT_IMAGE_UPLOAD_FOLDER',
        str(BASE_DIR / 'instance' / 'uploads' / 'products')
    )
    PRODUCT_IMAGE_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    PRODUCT_IMAGE_ALLOWED_MIMETYPES = {
        'image/png',
        'image/jpeg',
        'image/webp',
    }

    # Reverse proxy settings
    TRUST_PROXY_HEADERS = _get_bool_env('TRUST_PROXY_HEADERS', False)
    TRUST_PROXY_HOPS = _get_int_env('TRUST_PROXY_HOPS', 1)


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///ecommerce.db'
    )
    SQLALCHEMY_ECHO = True  # Log SQL queries
    
    # Less strict in development
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""
    
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory DB for tests
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration - enforces security best practices."""

    DEBUG = False
    TESTING = False

    # Database - required in production
    # Render fournit postgres:// mais SQLAlchemy 2.0 exige postgresql://
    _db_url = os.environ.get('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI = _db_url.replace('postgres://', 'postgresql://', 1) if _db_url else ''
    SQLALCHEMY_ECHO = False  # Do not log queries in production

    # Connection pool — évite l'épuisement des connexions sous forte charge
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': _get_int_env('DB_POOL_SIZE', 10),
        'max_overflow': _get_int_env('DB_MAX_OVERFLOW', 20),
        'pool_timeout': _get_int_env('DB_POOL_TIMEOUT', 30),
        'pool_recycle': _get_int_env('DB_POOL_RECYCLE', 1800),  # recycle toutes les 30 min
        'pool_pre_ping': True,  # vérifie la connexion avant utilisation
    }

    # Session security - strict in production
    SESSION_COOKIE_SECURE = _get_bool_env('SESSION_COOKIE_SECURE', True)
    SESSION_COOKIE_HTTPONLY = _get_bool_env('SESSION_COOKIE_HTTPONLY', True)
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Strict')

    # Rate Limiting - Redis si disponible, sinon memory://
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', os.environ.get('REDIS_URL', 'redis://localhost:6379'))


def _validate_production_config():
    """Validate production configuration on startup."""
    if os.environ.get('FLASK_ENV') != 'production':
        return  # Only validate in production
    
    # Check database URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError(
            "ERREUR: DATABASE_URL non définie en production. "
            "Définissez la variable d'environnement DATABASE_URL."
        )
    
    # Check secrets
    secret_key = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)
    if secret_key == DEFAULT_SECRET_KEY:
        raise ValueError(
            "ERREUR: SECRET_KEY utilise la valeur par défaut en production. "
            "Définissez une clé secrète forte via la variable d'environnement SECRET_KEY."
        )
    
    jwt_key = os.environ.get('JWT_SECRET_KEY')
    if not jwt_key or jwt_key == DEFAULT_SECRET_KEY:
        raise ValueError(
            "ERREUR: JWT_SECRET_KEY manquante ou utilise la valeur par défaut en production. "
            "Définissez une clé JWT forte via la variable d'environnement JWT_SECRET_KEY."
        )
    
    # Check rate limiter (memory:// accepté pour les déploiements sans Redis)
    storage_uri = os.environ.get('RATELIMIT_STORAGE_URI', os.environ.get('REDIS_URL', ''))
    if not storage_uri:
        raise ValueError(
            "ERREUR: RATELIMIT_STORAGE_URI non définie en production. "
            "Utilisez 'memory://' ou configurez Redis via REDIS_URL."
        )


# Configuration factory
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


def get_config():
    """Get configuration class based on FLASK_ENV."""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    if env not in config_by_name:
        raise ValueError(f"Environnement invalide: {env}. Choix: {list(config_by_name.keys())}")
    return config_by_name[env]
