"""
Tests for authentication endpoints:
  POST /auth/v1/register
  POST /auth/v1/login
  POST /auth/v1/refresh
  POST /auth/v1/logout
  GET  /auth/v1/me
"""

import pytest


REGISTER_URL = '/auth/v1/register'
LOGIN_URL    = '/auth/v1/login'
REFRESH_URL  = '/auth/v1/refresh'
LOGOUT_URL   = '/auth/v1/logout'
ME_URL       = '/auth/v1/me'

VALID_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'TestPassword123!',
    'nom': 'Dupont',
    'prenom': 'Jean',
}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegister:

    def test_register_success(self, client):
        res = client.post(REGISTER_URL, json=VALID_USER)
        assert res.status_code == 201
        assert res.get_json()['success'] is True

    def test_register_missing_required_fields(self, client):
        for field in ('username', 'email', 'password', 'nom', 'prenom'):
            payload = {k: v for k, v in VALID_USER.items() if k != field}
            res = client.post(REGISTER_URL, json=payload)
            assert res.status_code == 400, f"Missing field '{field}' should return 400"

    def test_register_empty_body(self, client):
        res = client.post(REGISTER_URL, json={})
        assert res.status_code == 400

    def test_register_returns_success_message(self, client):
        res = client.post(REGISTER_URL, json=VALID_USER)
        assert res.status_code == 201
        body = res.get_json()
        assert body['success'] is True
        assert 'message' in body

    def test_register_duplicate_email(self, client):
        client.post(REGISTER_URL, json=VALID_USER)
        payload = {**VALID_USER, 'username': 'otheruser'}
        res = client.post(REGISTER_URL, json=payload)
        assert res.status_code == 409

    def test_register_duplicate_username(self, client):
        client.post(REGISTER_URL, json=VALID_USER)
        payload = {**VALID_USER, 'email': 'other@example.com'}
        res = client.post(REGISTER_URL, json=payload)
        assert res.status_code == 409

    def test_register_requires_nom_and_prenom(self, client):
        """nom and prenom are required by the backend."""
        for field in ('nom', 'prenom'):
            payload = {k: v for k, v in VALID_USER.items() if k != field}
            res = client.post(REGISTER_URL, json=payload)
            assert res.status_code == 400, f"Field '{field}' should be required"


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:

    def _register(self, client):
        client.post(REGISTER_URL, json=VALID_USER)

    def test_login_with_email(self, client):
        self._register(client)
        res = client.post(LOGIN_URL, json={
            'email': VALID_USER['email'],
            'password': VALID_USER['password'],
        })
        assert res.status_code == 200
        data = res.get_json()['data']
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_login_with_username(self, client):
        self._register(client)
        res = client.post(LOGIN_URL, json={
            'email': VALID_USER['username'],
            'password': VALID_USER['password'],
        })
        assert res.status_code == 200

    def test_login_wrong_password(self, client):
        self._register(client)
        res = client.post(LOGIN_URL, json={
            'email': VALID_USER['email'],
            'password': 'WrongPassword999!',
        })
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        res = client.post(LOGIN_URL, json={
            'email': 'nobody@example.com',
            'password': 'TestPassword123!',
        })
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        res = client.post(LOGIN_URL, json={'email': VALID_USER['email']})
        assert res.status_code == 400

    def test_login_token_type_bearer(self, client):
        self._register(client)
        res = client.post(LOGIN_URL, json={
            'email': VALID_USER['email'],
            'password': VALID_USER['password'],
        })
        assert res.get_json()['data']['token_type'] == 'Bearer'


# ---------------------------------------------------------------------------
# Get me
# ---------------------------------------------------------------------------

class TestGetMe:

    def test_get_me_authenticated(self, client, auth_headers):
        res = client.get(ME_URL, headers=auth_headers)
        assert res.status_code == 200
        user = res.get_json()['data']
        assert 'email' in user
        assert 'username' in user
        assert 'password_hash' not in user

    def test_get_me_unauthenticated(self, client):
        assert client.get(ME_URL).status_code == 401

    def test_get_me_returns_correct_user(self, client, auth_headers):
        res = client.get(ME_URL, headers=auth_headers)
        user = res.get_json()['data']
        assert user['email'] == VALID_USER['email']


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class TestLogout:

    def test_logout_success(self, client, auth_headers):
        res = client.post(LOGOUT_URL, headers=auth_headers)
        assert res.status_code == 200

    def test_logout_invalidates_access_token(self, client, auth_headers):
        client.post(LOGOUT_URL, headers=auth_headers)
        res = client.get(ME_URL, headers=auth_headers)
        assert res.status_code == 401

    def test_logout_without_token(self, client):
        assert client.post(LOGOUT_URL).status_code == 401

    def test_double_logout_rejected(self, client, auth_headers):
        client.post(LOGOUT_URL, headers=auth_headers)
        res = client.post(LOGOUT_URL, headers=auth_headers)
        assert res.status_code == 401


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------

class TestRefresh:

    def _get_tokens(self, client):
        client.post(REGISTER_URL, json=VALID_USER)
        res = client.post(LOGIN_URL, json={
            'email': VALID_USER['email'],
            'password': VALID_USER['password'],
        })
        return res.get_json()['data']

    def test_refresh_returns_new_access_token(self, client):
        tokens = self._get_tokens(client)
        refresh_headers = {'Authorization': f"Bearer {tokens['refresh_token']}"}
        res = client.post(REFRESH_URL, headers=refresh_headers)
        assert res.status_code == 200
        assert 'access_token' in res.get_json()['data']

    def test_refresh_with_access_token_fails(self, client):
        tokens = self._get_tokens(client)
        access_headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        res = client.post(REFRESH_URL, headers=access_headers)
        # Access token cannot be used as refresh token
        assert res.status_code in (401, 422)

    def test_refresh_without_token(self, client):
        assert client.post(REFRESH_URL).status_code == 401
