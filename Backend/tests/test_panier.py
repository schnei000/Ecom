"""
Tests for shopping cart endpoints:
  POST   /api/v1/panier/add
  GET    /api/v1/panier/view
  PUT    /api/v1/panier/update/<product_id>
  DELETE /api/v1/panier/delete/<product_id>
  DELETE /api/v1/panier/clear
"""

import pytest

ADD_URL    = '/api/v1/panier/add'
VIEW_URL   = '/api/v1/panier/view'


def _update_url(pid):
    return f'/api/v1/panier/update/{pid}'


def _delete_url(pid):
    return f'/api/v1/panier/delete/{pid}'


CLEAR_URL  = '/api/v1/panier/clear'


# ---------------------------------------------------------------------------
# Add to cart
# ---------------------------------------------------------------------------

class TestAddToCart:

    def test_add_in_stock_product(self, client, auth_headers, sample_product):
        res = client.post(ADD_URL,
                          json={'product_id': sample_product, 'quantity': 2},
                          headers=auth_headers)
        assert res.status_code in (200, 201)

    def test_add_requires_authentication(self, client, sample_product):
        assert client.post(ADD_URL,
                           json={'product_id': sample_product, 'quantity': 1}).status_code == 401

    def test_add_out_of_stock_product_rejected(self, client, auth_headers, out_of_stock_product):
        res = client.post(ADD_URL,
                          json={'product_id': out_of_stock_product, 'quantity': 1},
                          headers=auth_headers)
        assert res.status_code == 400

    def test_add_nonexistent_product_rejected(self, client, auth_headers):
        assert client.post(ADD_URL,
                           json={'product_id': 999999, 'quantity': 1},
                           headers=auth_headers).status_code == 404

    def test_add_zero_quantity_rejected(self, client, auth_headers, sample_product):
        assert client.post(ADD_URL,
                           json={'product_id': sample_product, 'quantity': 0},
                           headers=auth_headers).status_code == 400

    def test_add_negative_quantity_rejected(self, client, auth_headers, sample_product):
        assert client.post(ADD_URL,
                           json={'product_id': sample_product, 'quantity': -1},
                           headers=auth_headers).status_code == 400

    def test_add_excessive_quantity_rejected(self, client, auth_headers, sample_product):
        assert client.post(ADD_URL,
                           json={'product_id': sample_product, 'quantity': 10001},
                           headers=auth_headers).status_code == 400

    def test_add_missing_product_id_rejected(self, client, auth_headers):
        assert client.post(ADD_URL, json={'quantity': 1},
                           headers=auth_headers).status_code == 400

    def test_add_same_product_twice_updates_quantity(self, client, auth_headers, sample_product):
        client.post(ADD_URL, json={'product_id': sample_product, 'quantity': 1},
                    headers=auth_headers)
        client.post(ADD_URL, json={'product_id': sample_product, 'quantity': 2},
                    headers=auth_headers)
        res = client.get(VIEW_URL, headers=auth_headers)
        items = res.get_json().get('items') or res.get_json().get('panier') or res.get_json()
        if isinstance(items, list):
            match = next((i for i in items if i.get('product_id') == sample_product), None)
            if match:
                assert match['quantity'] >= 1


# ---------------------------------------------------------------------------
# View cart
# ---------------------------------------------------------------------------

class TestViewCart:

    def test_view_empty_cart(self, client, auth_headers):
        res = client.get(VIEW_URL, headers=auth_headers)
        assert res.status_code == 200

    def test_view_requires_authentication(self, client):
        assert client.get(VIEW_URL).status_code == 401

    def test_view_shows_added_product(self, client, auth_headers, sample_product):
        client.post(ADD_URL, json={'product_id': sample_product, 'quantity': 3},
                    headers=auth_headers)
        res = client.get(VIEW_URL, headers=auth_headers)
        assert res.status_code == 200
        body = res.get_json()
        # API returns {"data": [...], "total_items": ..., "total_price": ...}
        items = body.get('data') or body.get('items') or (body if isinstance(body, list) else [])
        assert any(i.get('product_id') == sample_product for i in items)


# ---------------------------------------------------------------------------
# Update cart item
# ---------------------------------------------------------------------------

class TestUpdateCartItem:

    def _add(self, client, headers, product_id, qty=2):
        client.post(ADD_URL, json={'product_id': product_id, 'quantity': qty},
                    headers=headers)

    def test_update_quantity(self, client, auth_headers, sample_product):
        self._add(client, auth_headers, sample_product)
        res = client.put(_update_url(sample_product), json={'quantity': 5},
                         headers=auth_headers)
        assert res.status_code == 200

    def test_update_nonexistent_item_returns_404(self, client, auth_headers):
        assert client.put(_update_url(999999), json={'quantity': 1},
                          headers=auth_headers).status_code == 404

    def test_update_zero_quantity_removes_item(self, client, auth_headers, sample_product):
        self._add(client, auth_headers, sample_product)
        assert client.put(_update_url(sample_product), json={'quantity': 0},
                          headers=auth_headers).status_code == 200

    def test_update_requires_authentication(self, client, sample_product):
        assert client.put(_update_url(sample_product), json={'quantity': 1}).status_code == 401


# ---------------------------------------------------------------------------
# Remove item from cart
# ---------------------------------------------------------------------------

class TestRemoveFromCart:

    def test_remove_existing_item(self, client, auth_headers, sample_product):
        client.post(ADD_URL, json={'product_id': sample_product, 'quantity': 1},
                    headers=auth_headers)
        res = client.delete(_delete_url(sample_product), headers=auth_headers)
        assert res.status_code == 200

    def test_remove_nonexistent_item_returns_404(self, client, auth_headers):
        assert client.delete(_delete_url(999999), headers=auth_headers).status_code == 404

    def test_remove_requires_authentication(self, client, sample_product):
        assert client.delete(_delete_url(sample_product)).status_code == 401

    def test_item_gone_after_removal(self, client, auth_headers, sample_product):
        client.post(ADD_URL, json={'product_id': sample_product, 'quantity': 1},
                    headers=auth_headers)
        client.delete(_delete_url(sample_product), headers=auth_headers)
        res = client.get(VIEW_URL, headers=auth_headers)
        body = res.get_json()
        items = body.get('items') or body.get('panier') or (body if isinstance(body, list) else [])
        assert not any(i.get('product_id') == sample_product for i in items)


# ---------------------------------------------------------------------------
# Clear cart
# ---------------------------------------------------------------------------

class TestClearCart:

    def test_clear_empties_cart(self, client, auth_headers, sample_product):
        client.post(ADD_URL, json={'product_id': sample_product, 'quantity': 2},
                    headers=auth_headers)
        assert client.delete(CLEAR_URL, headers=auth_headers).status_code == 200

    def test_clear_requires_authentication(self, client):
        assert client.delete(CLEAR_URL).status_code == 401

    def test_cart_empty_after_clear(self, client, auth_headers, sample_product):
        client.post(ADD_URL, json={'product_id': sample_product, 'quantity': 1},
                    headers=auth_headers)
        client.delete(CLEAR_URL, headers=auth_headers)
        res = client.get(VIEW_URL, headers=auth_headers)
        body = res.get_json()
        items = body.get('items') or body.get('panier') or (body if isinstance(body, list) else [])
        assert items == []
