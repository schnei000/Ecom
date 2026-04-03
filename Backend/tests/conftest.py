"""
Pytest configuration and shared fixtures.
"""

import os
import pytest
from flask_bcrypt import Bcrypt
from app import create_app
from app.extension import db
from app.models import Category, Product, User

os.environ['FLASK_ENV'] = 'testing'
os.environ['FLASK_DEBUG'] = '0'


# ---------------------------------------------------------------------------
# App / client
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

def _register(client, username='testuser', email='test@example.com',
               password='TestPassword123!', nom='Test', prenom='User'):
    return client.post('/auth/v1/register', json={
        'username': username,
        'email': email,
        'password': password,
        'nom': nom,
        'prenom': prenom,
    })


def _login(client, email='test@example.com', password='TestPassword123!'):
    return client.post('/auth/v1/login', json={'email': email, 'password': password})


def _make_token(client, username='testuser', email='test@example.com',
                password='TestPassword123!'):
    _register(client, username=username, email=email, password=password)
    res = _login(client, email=email, password=password)
    assert res.status_code == 200
    return res.get_json()['data']['access_token']


def _make_admin_token(client, app):
    with app.app_context():
        bcrypt = Bcrypt(app)
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('AdminPass123!').decode('utf-8'),
            nom='Admin',
            prenom='Test',
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()
    res = _login(client, email='admin@example.com', password='AdminPass123!')
    assert res.status_code == 200
    return res.get_json()['data']['access_token']


# ---------------------------------------------------------------------------
# Auth header fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def auth_headers(client):
    token = _make_token(client)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(client, app):
    token = _make_admin_token(client, app)
    return {'Authorization': f'Bearer {token}'}


# ---------------------------------------------------------------------------
# Domain fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_category(app):
    with app.app_context():
        cat = Category(name='Électronique', description='Produits électroniques')
        db.session.add(cat)
        db.session.commit()
        return cat.id


@pytest.fixture
def sample_product(app, sample_category):
    with app.app_context():
        product = Product(
            name='Produit test',
            description='Description du produit test',
            price=49.99,
            stock=10,
            category_id=sample_category,
        )
        db.session.add(product)
        db.session.commit()
        return product.id


@pytest.fixture
def out_of_stock_product(app, sample_category):
    with app.app_context():
        product = Product(
            name='Produit épuisé',
            description='Stock zéro',
            price=9.99,
            stock=0,
            category_id=sample_category,
        )
        db.session.add(product)
        db.session.commit()
        return product.id
