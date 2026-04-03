"""
Security tests: authentication, input validation, rate limiting, admin access,
CSRF headers, data validation, JWT handling.
"""

import pytest
from app.extension import db
from app.models import Category, Product, User, TokenBlocklist
from datetime import datetime, timezone


class TestAuthenticationSecurity:

    def test_weak_password_registration_rejected(self, client):
        weak_passwords = [
            'short',
            'NoDigit!',
            'noupppercase1!',
            'NOLOWECASE1!',
            'NoSpecial123',
        ]
        for pwd in weak_passwords:
            res = client.post('/auth/v1/register', json={
                'username': 'testuser',
                'email': f'test_{pwd[:6]}@example.com',
                'password': pwd,
                'nom': 'Test',
                'prenom': 'User',
            })
            assert res.status_code == 400, f"Weak password '{pwd}' should be rejected"

    def test_strong_password_registration_accepted(self, client):
        res = client.post('/auth/v1/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        assert res.status_code == 201

    def test_invalid_email_rejected(self, client):
        invalid_emails = ['notanemail', 'missing@domain', '@domain.com', 'user@.com']
        for email in invalid_emails:
            res = client.post('/auth/v1/register', json={
                'username': 'testuser',
                'email': email,
                'password': 'TestPassword123!',
                'nom': 'Test',
                'prenom': 'User',
            })
            assert res.status_code == 400, f"Invalid email '{email}' should be rejected"

    def test_valid_email_accepted(self, client):
        res = client.post('/auth/v1/register', json={
            'username': 'testuser',
            'email': 'valid.email@example.com',
            'password': 'TestPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        assert res.status_code == 201

    def test_invalid_username_rejected(self, client):
        invalid_usernames = [
            'a',
            'a' * 81,
            'user-name',
            'user name',
            '_username',
            'username_',
            'user__name',
        ]
        for username in invalid_usernames:
            res = client.post('/auth/v1/register', json={
                'username': username,
                'email': f'u{abs(hash(username)) % 99999}@example.com',
                'password': 'TestPassword123!',
                'nom': 'Test',
                'prenom': 'User',
            })
            assert res.status_code == 400, f"Invalid username '{username}' should be rejected"

    def test_valid_username_accepted(self, client):
        res = client.post('/auth/v1/register', json={
            'username': 'valid_user_123',
            'email': 'valid@example.com',
            'password': 'TestPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        assert res.status_code == 201

    def test_duplicate_email_rejected(self, client):
        for username in ('user1', 'user2'):
            client.post('/auth/v1/register', json={
                'username': username,
                'email': 'duplicate@example.com',
                'password': 'TestPassword123!',
                'nom': 'Test',
                'prenom': 'User',
            })
        res = client.post('/auth/v1/register', json={
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'TestPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        assert res.status_code == 409

    def test_duplicate_username_rejected(self, client):
        client.post('/auth/v1/register', json={
            'username': 'dup_user',
            'email': 'user1@example.com',
            'password': 'TestPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        res = client.post('/auth/v1/register', json={
            'username': 'dup_user',
            'email': 'user2@example.com',
            'password': 'TestPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        assert res.status_code == 409

    def test_login_with_invalid_credentials(self, client):
        client.post('/auth/v1/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        res = client.post('/auth/v1/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword123!',
        })
        assert res.status_code == 401

    def test_login_returns_tokens(self, client):
        client.post('/auth/v1/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        res = client.post('/auth/v1/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
        })
        assert res.status_code == 200
        data = res.get_json()['data']
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data.get('token_type') == 'Bearer'

    def test_logout_invalidates_token(self, client, auth_headers):
        assert client.get('/auth/v1/me', headers=auth_headers).status_code == 200
        assert client.post('/auth/v1/logout', headers=auth_headers).status_code == 200
        assert client.get('/auth/v1/me', headers=auth_headers).status_code == 401


class TestInputValidation:

    def test_sql_injection_in_panier_rejected(self, client, auth_headers):
        res = client.post('/api/v1/panier/add',
            json={'product_id': "1; DROP TABLE products;", 'quantity': 1},
            headers=auth_headers,
        )
        assert res.status_code == 400

    def test_invalid_quantity_rejected(self, client, auth_headers):
        for qty in [-1, 0, 'not_a_number', 10001]:
            res = client.post('/api/v1/panier/add',
                json={'product_id': 1, 'quantity': qty},
                headers=auth_headers,
            )
            assert res.status_code in (400, 404), f"Quantity {qty} should be rejected"

    def test_xss_in_product_name_sanitized(self, client, admin_headers, sample_category):
        xss = '<script>alert("xss")</script>'
        res = client.post('/api/v1/products',
            json={
                'name': xss,
                'description': 'Test',
                'price': 10.0,
                'stock': 100,
                'category_id': sample_category,
            },
            headers=admin_headers,
        )
        if res.status_code == 201:
            name = res.get_json()['data']['name']
            assert '<script>' not in name


class TestRateLimiting:

    def test_registration_rate_limit(self, client):
        responses = []
        for i in range(15):
            res = client.post('/auth/v1/register', json={
                'username': f'user{i}',
                'email': f'user{i}@example.com',
                'password': 'TestPassword123!',
                'nom': 'Test',
                'prenom': 'User',
            })
            responses.append(res.status_code)
        assert 429 in responses

    def test_login_rate_limit(self, client):
        client.post('/auth/v1/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'nom': 'Test',
            'prenom': 'User',
        })
        responses = []
        for i in range(10):
            res = client.post('/auth/v1/login', json={
                'email': 'test@example.com',
                'password': f'WrongPassword{i}!',
            })
            responses.append(res.status_code)
        assert 429 in responses


class TestAdminAccess:

    def test_non_admin_cannot_create_product(self, client, auth_headers, sample_category):
        res = client.post('/api/v1/products',
            json={
                'name': 'Test Product',
                'description': 'Test',
                'price': 10.0,
                'stock': 100,
                'category_id': sample_category,
            },
            headers=auth_headers,
        )
        assert res.status_code == 403

    def test_non_admin_cannot_delete_product(self, client, auth_headers, sample_product):
        res = client.delete(f'/api/v1/products/{sample_product}', headers=auth_headers)
        assert res.status_code == 403

    def test_non_admin_cannot_list_users(self, client, auth_headers):
        res = client.get('/auth/v1/users', headers=auth_headers)
        assert res.status_code == 403

    def test_unauthenticated_cannot_access_admin_routes(self, client):
        assert client.post('/api/v1/products', json={}).status_code == 401
        assert client.get('/auth/v1/users').status_code == 401


class TestSecurityHeaders:

    def test_owasp_headers_present(self, client):
        res = client.get('/')
        assert res.headers.get('X-Frame-Options') == 'DENY'
        assert res.headers.get('X-Content-Type-Options') == 'nosniff'
        assert 'X-XSS-Protection' in res.headers


class TestDataValidation:

    def test_negative_price_rejected(self, client, admin_headers, sample_category):
        res = client.post('/api/v1/products',
            json={'name': 'Test', 'description': 'Test', 'price': -10.0,
                  'stock': 100, 'category_id': sample_category},
            headers=admin_headers,
        )
        assert res.status_code == 400

    def test_negative_stock_rejected(self, client, admin_headers, sample_category):
        res = client.post('/api/v1/products',
            json={'name': 'Test', 'description': 'Test', 'price': 10.0,
                  'stock': -100, 'category_id': sample_category},
            headers=admin_headers,
        )
        assert res.status_code == 400

    def test_invalid_price_format_rejected(self, client, admin_headers, sample_category):
        res = client.post('/api/v1/products',
            json={'name': 'Test', 'description': 'Test', 'price': 'not_a_number',
                  'stock': 100, 'category_id': sample_category},
            headers=admin_headers,
        )
        assert res.status_code == 400


class TestJWTTokenHandling:

    def test_missing_token_rejected(self, client):
        assert client.get('/auth/v1/me').status_code == 401

    def test_invalid_token_rejected(self, client):
        res = client.get('/auth/v1/me', headers={'Authorization': 'Bearer invalid_token'})
        # Flask-JWT-Extended returns 422 for structurally invalid tokens
        assert res.status_code in (401, 422)

    def test_malformed_token_rejected(self, client):
        res = client.get('/auth/v1/me', headers={'Authorization': 'Bearer this.is.not.valid.jwt'})
        assert res.status_code in (401, 422)
