"""
Tests for product endpoints:
  GET   /api/v1/products
  GET   /api/v1/products/<id>
  POST  /api/v1/products           (admin)
  PUT   /api/v1/products/<id>      (admin)
  DELETE /api/v1/products/<id>     (admin)
  PATCH /api/v1/products/<id>/stock (admin)
"""

import pytest
from app.extension import db
from app.models import Product

PRODUCTS_URL = '/api/v1/products'


def _product_url(pid):
    return f'{PRODUCTS_URL}/{pid}'


def _stock_url(pid):
    return f'{PRODUCTS_URL}/{pid}/stock'


def _make_payload(category_id, name='Nouveau produit'):
    return {
        'name': name,
        'description': 'Description complète du produit.',
        'price': 29.99,
        'stock': 50,
        'category_id': category_id,
    }


# ---------------------------------------------------------------------------
# List products
# ---------------------------------------------------------------------------

class TestListProducts:

    def test_list_products_public(self, client):
        res = client.get(PRODUCTS_URL)
        assert res.status_code == 200
        assert 'data' in res.get_json()

    def test_list_products_is_array(self, client, sample_product):
        res = client.get(PRODUCTS_URL)
        assert isinstance(res.get_json()['data'], list)

    def test_list_includes_created_product(self, client, sample_product):
        res = client.get(PRODUCTS_URL)
        ids = [p['id'] for p in res.get_json()['data']]
        assert sample_product in ids

    def test_filter_by_category(self, client, sample_product, sample_category):
        res = client.get(f'{PRODUCTS_URL}?category_id={sample_category}')
        assert res.status_code == 200
        for p in res.get_json()['data']:
            assert p['category_id'] == sample_category

    def test_search_by_name(self, client, sample_product):
        res = client.get(f'{PRODUCTS_URL}?search=Produit+test')
        assert res.status_code == 200
        assert any('Produit test' in p['name'] for p in res.get_json()['data'])

    def test_search_no_match_returns_empty(self, client):
        res = client.get(f'{PRODUCTS_URL}?search=zzz_nomatch_zzz')
        assert res.status_code == 200
        assert res.get_json()['data'] == []

    def test_pagination_per_page(self, client, sample_product):
        res = client.get(f'{PRODUCTS_URL}?page=1&per_page=1')
        assert res.status_code == 200
        assert len(res.get_json()['data']) <= 1

    def test_deleted_product_hidden_in_list(self, client, admin_headers, sample_product):
        client.delete(_product_url(sample_product), headers=admin_headers)
        res = client.get(PRODUCTS_URL)
        ids = [p['id'] for p in res.get_json()['data']]
        assert sample_product not in ids


# ---------------------------------------------------------------------------
# Get single product
# ---------------------------------------------------------------------------

class TestGetProduct:

    def test_get_existing_product(self, client, sample_product):
        res = client.get(_product_url(sample_product))
        assert res.status_code == 200
        assert res.get_json()['data']['id'] == sample_product

    def test_get_nonexistent_product(self, client):
        assert client.get(_product_url(999999)).status_code == 404

    def test_product_has_expected_fields(self, client, sample_product):
        data = client.get(_product_url(sample_product)).get_json()['data']
        for field in ('id', 'name', 'description', 'price', 'stock', 'category_id'):
            assert field in data, f"Missing field '{field}'"


# ---------------------------------------------------------------------------
# Create product (admin)
# ---------------------------------------------------------------------------

class TestCreateProduct:

    def test_admin_creates_product(self, client, admin_headers, sample_category):
        res = client.post(PRODUCTS_URL, json=_make_payload(sample_category),
                          headers=admin_headers)
        assert res.status_code == 201
        assert res.get_json()['data']['name'] == 'Nouveau produit'

    def test_non_admin_cannot_create(self, client, auth_headers, sample_category):
        assert client.post(PRODUCTS_URL, json=_make_payload(sample_category),
                           headers=auth_headers).status_code == 403

    def test_unauthenticated_cannot_create(self, client, sample_category):
        assert client.post(PRODUCTS_URL, json=_make_payload(sample_category)).status_code == 401

    def test_create_missing_name(self, client, admin_headers, sample_category):
        payload = _make_payload(sample_category)
        del payload['name']
        assert client.post(PRODUCTS_URL, json=payload, headers=admin_headers).status_code == 400

    def test_create_missing_category(self, client, admin_headers):
        payload = {'name': 'Sans cat', 'description': 'X', 'price': 5, 'stock': 1}
        assert client.post(PRODUCTS_URL, json=payload, headers=admin_headers).status_code == 400

    def test_create_negative_price_rejected(self, client, admin_headers, sample_category):
        payload = {**_make_payload(sample_category), 'price': -1}
        assert client.post(PRODUCTS_URL, json=payload, headers=admin_headers).status_code == 400

    def test_create_negative_stock_rejected(self, client, admin_headers, sample_category):
        payload = {**_make_payload(sample_category), 'stock': -5}
        assert client.post(PRODUCTS_URL, json=payload, headers=admin_headers).status_code == 400

    def test_create_duplicate_name_rejected(self, client, admin_headers, sample_product, sample_category):
        payload = {**_make_payload(sample_category), 'name': 'Produit test'}
        assert client.post(PRODUCTS_URL, json=payload, headers=admin_headers).status_code == 409

    def test_create_zero_price_allowed(self, client, admin_headers, sample_category):
        payload = {**_make_payload(sample_category), 'name': 'Gratuit', 'price': 0}
        assert client.post(PRODUCTS_URL, json=payload, headers=admin_headers).status_code == 201

    def test_create_zero_stock_allowed(self, client, admin_headers, sample_category):
        payload = {**_make_payload(sample_category), 'name': 'Rupture', 'stock': 0}
        assert client.post(PRODUCTS_URL, json=payload, headers=admin_headers).status_code == 201


# ---------------------------------------------------------------------------
# Update product (admin)
# ---------------------------------------------------------------------------

class TestUpdateProduct:

    def test_admin_updates_product(self, client, admin_headers, sample_product):
        res = client.put(_product_url(sample_product),
                         json={'name': 'Produit test', 'description': 'Nouvelle desc',
                               'price': 99.99, 'stock': 5},
                         headers=admin_headers)
        assert res.status_code == 200
        data = res.get_json()['data']
        assert data['description'] == 'Nouvelle desc'
        assert float(data['price']) == 99.99

    def test_non_admin_cannot_update(self, client, auth_headers, sample_product):
        assert client.put(_product_url(sample_product), json={'name': 'X'},
                          headers=auth_headers).status_code == 403

    def test_update_nonexistent_product(self, client, admin_headers, sample_category):
        assert client.put(_product_url(999999),
                          json=_make_payload(sample_category),
                          headers=admin_headers).status_code == 404

    def test_patch_method_works(self, client, admin_headers, sample_product):
        res = client.patch(_product_url(sample_product),
                           json={'stock': 99},
                           headers=admin_headers)
        assert res.status_code == 200


# ---------------------------------------------------------------------------
# Delete product (admin)
# ---------------------------------------------------------------------------

class TestDeleteProduct:

    def test_admin_deletes_product(self, client, admin_headers, sample_product):
        res = client.delete(_product_url(sample_product), headers=admin_headers)
        assert res.status_code == 200

    def test_deleted_product_returns_404(self, client, admin_headers, sample_product):
        client.delete(_product_url(sample_product), headers=admin_headers)
        assert client.get(_product_url(sample_product)).status_code == 404

    def test_non_admin_cannot_delete(self, client, auth_headers, sample_product):
        assert client.delete(_product_url(sample_product),
                             headers=auth_headers).status_code == 403

    def test_delete_nonexistent_product(self, client, admin_headers):
        assert client.delete(_product_url(999999), headers=admin_headers).status_code == 404


# ---------------------------------------------------------------------------
# Stock adjustment (admin)
# ---------------------------------------------------------------------------

class TestStockAdjust:

    def test_adjust_stock_positive_delta(self, client, admin_headers, sample_product):
        initial = client.get(_product_url(sample_product)).get_json()['data']['stock']
        res = client.patch(_stock_url(sample_product), json={'delta': 5},
                           headers=admin_headers)
        assert res.status_code == 200
        assert res.get_json()['data']['new_stock'] == initial + 5

    def test_adjust_stock_negative_delta(self, client, admin_headers, sample_product):
        initial = client.get(_product_url(sample_product)).get_json()['data']['stock']
        res = client.patch(_stock_url(sample_product), json={'delta': -3},
                           headers=admin_headers)
        assert res.status_code == 200
        assert res.get_json()['data']['new_stock'] == initial - 3

    def test_adjust_stock_cannot_go_below_zero(self, client, admin_headers, sample_product):
        res = client.patch(_stock_url(sample_product), json={'delta': -9999},
                           headers=admin_headers)
        assert res.status_code == 400

    def test_adjust_stock_non_admin_rejected(self, client, auth_headers, sample_product):
        assert client.patch(_stock_url(sample_product), json={'delta': 1},
                            headers=auth_headers).status_code == 403

    def test_adjust_stock_missing_delta_rejected(self, client, admin_headers, sample_product):
        assert client.patch(_stock_url(sample_product), json={},
                            headers=admin_headers).status_code == 400
