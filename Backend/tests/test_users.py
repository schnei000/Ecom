"""
Tests for user management endpoints:
  GET   /auth/v1/me
  PUT   /auth/v1/me
  PATCH /auth/v1/me/password
  POST  /auth/v1/me/delete
  GET   /auth/v1/users  (admin)
"""

import pytest

ME_URL       = '/auth/v1/me'
PW_URL       = '/auth/v1/me/password'
DELETE_URL   = '/auth/v1/me/delete'
USERS_URL    = '/auth/v1/users'
REGISTER_URL = '/auth/v1/register'
LOGIN_URL    = '/auth/v1/login'

VALID_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'TestPassword123!',
    'nom': 'Dupont',
    'prenom': 'Jean',
}


# ---------------------------------------------------------------------------
# Profile update
# ---------------------------------------------------------------------------

class TestUpdateProfile:

    def test_update_prenom_nom(self, client, auth_headers):
        res = client.put(ME_URL, json={'prenom': 'Marie', 'nom': 'Martin'},
                         headers=auth_headers)
        assert res.status_code == 200
        user = res.get_json()['data']
        assert user['prenom'] == 'Marie'
        assert user['nom'] == 'Martin'

    def test_update_email(self, client, auth_headers):
        res = client.put(ME_URL, json={'email': 'new@example.com'}, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()['data']['email'] == 'new@example.com'

    def test_update_username(self, client, auth_headers):
        res = client.put(ME_URL, json={'username': 'newname123'}, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()['data']['username'] == 'newname123'

    def test_update_email_conflict(self, client, auth_headers):
        client.post(REGISTER_URL, json={
            'username': 'other',
            'email': 'other@example.com',
            'password': 'TestPassword123!',
            'nom': 'A',
            'prenom': 'B',
        })
        res = client.put(ME_URL, json={'email': 'other@example.com'}, headers=auth_headers)
        assert res.status_code == 409

    def test_update_username_conflict(self, client, auth_headers):
        client.post(REGISTER_URL, json={
            'username': 'occupied',
            'email': 'occ@example.com',
            'password': 'TestPassword123!',
            'nom': 'A',
            'prenom': 'B',
        })
        res = client.put(ME_URL, json={'username': 'occupied'}, headers=auth_headers)
        assert res.status_code == 409

    def test_update_invalid_email_rejected(self, client, auth_headers):
        res = client.put(ME_URL, json={'email': 'notanemail'}, headers=auth_headers)
        assert res.status_code == 400

    def test_update_invalid_username_rejected(self, client, auth_headers):
        res = client.put(ME_URL, json={'username': 'a'}, headers=auth_headers)
        assert res.status_code == 400

    def test_update_without_auth(self, client):
        assert client.put(ME_URL, json={'prenom': 'Test'}).status_code == 401

    def test_patch_method_also_works(self, client, auth_headers):
        res = client.patch(ME_URL, json={'prenom': 'PatchedName'}, headers=auth_headers)
        assert res.status_code == 200


# ---------------------------------------------------------------------------
# Password change
# ---------------------------------------------------------------------------

class TestChangePassword:

    def test_change_password_success(self, client, auth_headers):
        res = client.patch(PW_URL, json={
            'current_password': VALID_USER['password'],
            'new_password': 'NewSecurePass456!',
        }, headers=auth_headers)
        assert res.status_code == 200

    def test_wrong_current_password_rejected(self, client, auth_headers):
        res = client.patch(PW_URL, json={
            'current_password': 'WrongPass123!',
            'new_password': 'NewSecurePass456!',
        }, headers=auth_headers)
        assert res.status_code in (400, 401)

    def test_weak_new_password_rejected(self, client, auth_headers):
        res = client.patch(PW_URL, json={
            'current_password': VALID_USER['password'],
            'new_password': 'weak',
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_same_password_rejected(self, client, auth_headers):
        res = client.patch(PW_URL, json={
            'current_password': VALID_USER['password'],
            'new_password': VALID_USER['password'],
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_missing_fields_rejected(self, client, auth_headers):
        res = client.patch(PW_URL, json={'current_password': VALID_USER['password']},
                           headers=auth_headers)
        assert res.status_code == 400

    def test_change_password_without_auth(self, client):
        assert client.patch(PW_URL, json={}).status_code == 401

    def test_new_password_works_for_login(self, client, auth_headers):
        new_pw = 'NewSecurePass456!'
        client.patch(PW_URL, json={
            'current_password': VALID_USER['password'],
            'new_password': new_pw,
        }, headers=auth_headers)
        res = client.post(LOGIN_URL, json={
            'email': VALID_USER['email'],
            'password': new_pw,
        })
        assert res.status_code == 200


# ---------------------------------------------------------------------------
# Account deletion (soft)
# ---------------------------------------------------------------------------

class TestDeleteAccount:

    def _get_fresh_headers(self, client, email='del@example.com', pw='TestPassword123!',
                           username='todelete'):
        client.post(REGISTER_URL, json={
            'username': username,
            'email': email,
            'password': pw,
            'nom': 'Del',
            'prenom': 'Test',
        })
        res = client.post(LOGIN_URL, json={'email': email, 'password': pw})
        token = res.get_json()['data']['access_token']
        return {'Authorization': f'Bearer {token}'}

    def test_delete_with_correct_password(self, client):
        headers = self._get_fresh_headers(client, email='del1@example.com', username='todel1')
        res = client.post(DELETE_URL, json={'password': 'TestPassword123!'}, headers=headers)
        assert res.status_code == 200

    def test_delete_with_wrong_password(self, client):
        headers = self._get_fresh_headers(client, email='del2@example.com', username='todel2')
        res = client.post(DELETE_URL, json={'password': 'Wrong999!'}, headers=headers)
        assert res.status_code in (400, 401)

    def test_deleted_token_invalid(self, client):
        headers = self._get_fresh_headers(client, email='del3@example.com', username='todel3')
        client.post(DELETE_URL, json={'password': 'TestPassword123!'}, headers=headers)
        res = client.get(ME_URL, headers=headers)
        assert res.status_code == 401

    def test_delete_without_auth(self, client):
        assert client.post(DELETE_URL, json={'password': 'x'}).status_code == 401


# ---------------------------------------------------------------------------
# Admin — list users
# ---------------------------------------------------------------------------

class TestListUsers:

    def test_admin_can_list_users(self, client, admin_headers):
        res = client.get(USERS_URL, headers=admin_headers)
        assert res.status_code == 200
        assert isinstance(res.get_json()['data'], list)

    def test_non_admin_cannot_list_users(self, client, auth_headers):
        assert client.get(USERS_URL, headers=auth_headers).status_code == 403

    def test_unauthenticated_cannot_list_users(self, client):
        assert client.get(USERS_URL).status_code == 401

    def test_list_users_pagination(self, client, admin_headers):
        res = client.get(f'{USERS_URL}?page=1&per_page=5', headers=admin_headers)
        assert res.status_code == 200
