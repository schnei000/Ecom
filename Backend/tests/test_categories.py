"""
Tests for category endpoints:
  GET   /api/v1/categories
  GET   /api/v1/categories/<id>
  GET   /api/v1/categories/<id>/products
  POST  /api/v1/categories           (admin)
  PUT   /api/v1/categories/<id>      (admin)
  DELETE /api/v1/categories/<id>     (admin)
"""

import pytest
from app.extension import db
from app.models import Category

CATEGORIES_URL = '/api/v1/categories'


def _cat_url(cid):
    return f'{CATEGORIES_URL}/{cid}'


def _products_url(cid):
    return f'{CATEGORIES_URL}/{cid}/products'


# ---------------------------------------------------------------------------
# List categories
# ---------------------------------------------------------------------------

class TestListCategories:

    def test_list_public(self, client):
        res = client.get(CATEGORIES_URL)
        assert res.status_code == 200
        assert 'data' in res.get_json()

    def test_list_returns_array(self, client, sample_category):
        assert isinstance(client.get(CATEGORIES_URL).get_json()['data'], list)

    def test_list_includes_created_category(self, client, sample_category):
        ids = [c['id'] for c in client.get(CATEGORIES_URL).get_json()['data']]
        assert sample_category in ids

    def test_pagination_supported(self, client, sample_category):
        res = client.get(f'{CATEGORIES_URL}?page=1&per_page=5')
        assert res.status_code == 200


# ---------------------------------------------------------------------------
# Get single category
# ---------------------------------------------------------------------------

class TestGetCategory:

    def test_get_existing(self, client, sample_category):
        res = client.get(_cat_url(sample_category))
        assert res.status_code == 200
        assert res.get_json()['data']['id'] == sample_category

    def test_get_nonexistent(self, client):
        assert client.get(_cat_url(999999)).status_code == 404

    def test_has_expected_fields(self, client, sample_category):
        data = client.get(_cat_url(sample_category)).get_json()['data']
        assert 'id' in data
        assert 'name' in data


# ---------------------------------------------------------------------------
# Products by category
# ---------------------------------------------------------------------------

class TestProductsByCategory:

    def test_products_by_category(self, client, sample_product, sample_category):
        res = client.get(_products_url(sample_category))
        assert res.status_code == 200
        assert isinstance(res.get_json()['data'], list)
        for p in res.get_json()['data']:
            assert p['category_id'] == sample_category

    def test_nonexistent_category_returns_404(self, client):
        assert client.get(_products_url(999999)).status_code == 404


# ---------------------------------------------------------------------------
# Create category (admin)
# ---------------------------------------------------------------------------

class TestCreateCategory:

    def test_admin_creates_category(self, client, admin_headers):
        res = client.post(CATEGORIES_URL,
                          json={'name': 'Vêtements', 'description': 'Mode'},
                          headers=admin_headers)
        assert res.status_code == 201
        assert res.get_json()['data']['name'] == 'Vêtements'

    def test_create_without_description(self, client, admin_headers):
        res = client.post(CATEGORIES_URL, json={'name': 'SansDesc'}, headers=admin_headers)
        assert res.status_code == 201

    def test_create_missing_name_rejected(self, client, admin_headers):
        assert client.post(CATEGORIES_URL, json={'description': 'X'},
                           headers=admin_headers).status_code == 400

    def test_duplicate_name_rejected(self, client, admin_headers, sample_category):
        res = client.post(CATEGORIES_URL, json={'name': 'Électronique'},
                          headers=admin_headers)
        assert res.status_code == 409

    def test_non_admin_cannot_create(self, client, auth_headers):
        assert client.post(CATEGORIES_URL, json={'name': 'Test'},
                           headers=auth_headers).status_code == 403

    def test_unauthenticated_cannot_create(self, client):
        assert client.post(CATEGORIES_URL, json={'name': 'Test'}).status_code == 401


# ---------------------------------------------------------------------------
# Update category (admin)
# ---------------------------------------------------------------------------

class TestUpdateCategory:

    def test_admin_updates_name(self, client, admin_headers, sample_category):
        res = client.put(_cat_url(sample_category), json={'name': 'Nouveau nom'},
                         headers=admin_headers)
        assert res.status_code == 200
        assert res.get_json()['data']['name'] == 'Nouveau nom'

    def test_admin_updates_description(self, client, admin_headers, sample_category):
        res = client.put(_cat_url(sample_category), json={'description': 'Nouvelle desc'},
                         headers=admin_headers)
        assert res.status_code == 200

    def test_patch_method_works(self, client, admin_headers, sample_category):
        res = client.patch(_cat_url(sample_category), json={'description': 'Patched'},
                           headers=admin_headers)
        assert res.status_code == 200

    def test_non_admin_cannot_update(self, client, auth_headers, sample_category):
        assert client.put(_cat_url(sample_category), json={'name': 'X'},
                          headers=auth_headers).status_code == 403

    def test_update_nonexistent_returns_404(self, client, admin_headers):
        assert client.put(_cat_url(999999), json={'name': 'X'},
                          headers=admin_headers).status_code == 404

    def test_name_conflict_on_update_rejected(self, client, admin_headers):
        # Create two categories
        res1 = client.post(CATEGORIES_URL, json={'name': 'CatA'}, headers=admin_headers)
        res2 = client.post(CATEGORIES_URL, json={'name': 'CatB'}, headers=admin_headers)
        id_b = res2.get_json()['data']['id']
        # Try to rename CatB to CatA
        assert client.put(_cat_url(id_b), json={'name': 'CatA'},
                          headers=admin_headers).status_code == 409


# ---------------------------------------------------------------------------
# Delete category (admin)
# ---------------------------------------------------------------------------

class TestDeleteCategory:

    def test_admin_deletes_empty_category(self, client, admin_headers):
        res = client.post(CATEGORIES_URL, json={'name': 'ToDelete'}, headers=admin_headers)
        cid = res.get_json()['data']['id']
        assert client.delete(_cat_url(cid), headers=admin_headers).status_code == 200

    def test_deleted_category_not_found(self, client, admin_headers):
        res = client.post(CATEGORIES_URL, json={'name': 'Gone'}, headers=admin_headers)
        cid = res.get_json()['data']['id']
        client.delete(_cat_url(cid), headers=admin_headers)
        assert client.get(_cat_url(cid)).status_code == 404

    def test_cannot_delete_category_with_active_products(self, client, admin_headers,
                                                          sample_product, sample_category):
        res = client.delete(_cat_url(sample_category), headers=admin_headers)
        assert res.status_code == 400

    def test_non_admin_cannot_delete(self, client, auth_headers, sample_category):
        assert client.delete(_cat_url(sample_category),
                             headers=auth_headers).status_code == 403

    def test_delete_nonexistent_returns_404(self, client, admin_headers):
        assert client.delete(_cat_url(999999), headers=admin_headers).status_code == 404
