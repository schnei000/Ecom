"""
Tests for order endpoints:
  POST /api/v1/order
  GET  /api/v1/orders
  GET  /api/v1/orders/<id>
  POST /api/v1/orders/<id>/cancel
"""

import pytest

ORDER_URL  = '/api/v1/order'
ORDERS_URL = '/api/v1/orders'
ADD_URL    = '/api/v1/panier/add'


def _order_url(oid):
    return f'{ORDERS_URL}/{oid}'


def _cancel_url(oid):
    return f'{ORDERS_URL}/{oid}/cancel'


def _fill_cart(client, headers, product_id, qty=1):
    """Add a product to the user's cart."""
    client.post(ADD_URL, json={'product_id': product_id, 'quantity': qty}, headers=headers)


def _create_order(client, headers):
    """Create an order from the current cart and return the response."""
    return client.post(ORDER_URL, headers=headers)


# ---------------------------------------------------------------------------
# Create order
# ---------------------------------------------------------------------------

class TestCreateOrder:

    def test_create_order_from_cart(self, client, auth_headers, sample_product):
        _fill_cart(client, auth_headers, sample_product)
        res = _create_order(client, auth_headers)
        assert res.status_code == 201

    def test_create_order_returns_order_id(self, client, auth_headers, sample_product):
        _fill_cart(client, auth_headers, sample_product)
        res = _create_order(client, auth_headers)
        assert 'order_id' in res.get_json().get('data', {})

    def test_create_order_with_empty_cart_rejected(self, client, auth_headers):
        res = _create_order(client, auth_headers)
        assert res.status_code == 400

    def test_create_order_requires_authentication(self, client):
        assert client.post(ORDER_URL).status_code == 401

    def test_cart_cleared_after_order(self, client, auth_headers, sample_product):
        _fill_cart(client, auth_headers, sample_product)
        _create_order(client, auth_headers)
        cart_res = client.get('/api/v1/panier/view', headers=auth_headers)
        body = cart_res.get_json()
        items = body.get('items') or body.get('panier') or (body if isinstance(body, list) else [])
        assert items == []

    def test_cannot_create_duplicate_pending_order(self, client, auth_headers, sample_product):
        _fill_cart(client, auth_headers, sample_product)
        _create_order(client, auth_headers)
        # Refill cart and try again while first order is pending
        _fill_cart(client, auth_headers, sample_product)
        res = _create_order(client, auth_headers)
        assert res.status_code == 400

    def test_order_reduces_stock(self, client, auth_headers, admin_headers,
                                  sample_product):
        from app.extension import db
        initial_res = client.get(f'/api/v1/products/{sample_product}')
        initial_stock = initial_res.get_json()['data']['stock']

        _fill_cart(client, auth_headers, sample_product, qty=2)
        _create_order(client, auth_headers)

        after_res = client.get(f'/api/v1/products/{sample_product}')
        after_stock = after_res.get_json()['data']['stock']
        assert after_stock == initial_stock - 2


# ---------------------------------------------------------------------------
# List orders
# ---------------------------------------------------------------------------

class TestListOrders:

    def test_list_returns_array(self, client, auth_headers):
        res = client.get(ORDERS_URL, headers=auth_headers)
        assert res.status_code == 200
        body = res.get_json()
        orders = body.get('data') if isinstance(body, dict) else body
        assert isinstance(orders, list)

    def test_list_requires_authentication(self, client):
        assert client.get(ORDERS_URL).status_code == 401

    def test_user_sees_own_orders(self, client, auth_headers, sample_product):
        _fill_cart(client, auth_headers, sample_product)
        _create_order(client, auth_headers)
        body = client.get(ORDERS_URL, headers=auth_headers).get_json()
        orders = body.get('data') if isinstance(body, dict) else body
        assert len(orders) == 1

    def test_user_does_not_see_other_user_orders(self, client, auth_headers,
                                                  admin_headers, sample_product):
        _fill_cart(client, admin_headers, sample_product)
        _create_order(client, admin_headers)
        body = client.get(ORDERS_URL, headers=auth_headers).get_json()
        orders = body.get('data') if isinstance(body, dict) else body
        assert len(orders) == 0


# ---------------------------------------------------------------------------
# Get single order
# ---------------------------------------------------------------------------

class TestGetOrder:

    def test_get_own_order(self, client, auth_headers, sample_product):
        _fill_cart(client, auth_headers, sample_product)
        order_id = _create_order(client, auth_headers).get_json()['data']['order_id']
        res = client.get(_order_url(order_id), headers=auth_headers)
        assert res.status_code == 200

    def test_get_nonexistent_order(self, client, auth_headers):
        assert client.get(_order_url(999999), headers=auth_headers).status_code == 404

    def test_get_other_user_order_denied(self, client, auth_headers, admin_headers,
                                          sample_product):
        _fill_cart(client, admin_headers, sample_product)
        order_id = _create_order(client, admin_headers).get_json()['data']['order_id']
        assert client.get(_order_url(order_id), headers=auth_headers).status_code in (403, 404)


# ---------------------------------------------------------------------------
# Cancel order
# ---------------------------------------------------------------------------

class TestCancelOrder:

    def test_cancel_pending_order(self, client, auth_headers, sample_product):
        _fill_cart(client, auth_headers, sample_product)
        order_id = _create_order(client, auth_headers).get_json()['data']['order_id']
        res = client.post(_cancel_url(order_id), headers=auth_headers)
        assert res.status_code == 200

    def test_cancelled_order_status_updated(self, client, auth_headers, sample_product):
        _fill_cart(client, auth_headers, sample_product)
        order_id = _create_order(client, auth_headers).get_json()['data']['order_id']
        client.post(_cancel_url(order_id), headers=auth_headers)
        order = client.get(_order_url(order_id), headers=auth_headers).get_json()
        status = (order.get('data') or order).get('status')
        assert status == 'cancelled'

    def test_cancel_nonexistent_order(self, client, auth_headers):
        assert client.post(_cancel_url(999999), headers=auth_headers).status_code == 404

    def test_cancel_requires_authentication(self, client):
        assert client.post(_cancel_url(1)).status_code == 401

    def test_cannot_cancel_other_user_order(self, client, auth_headers, admin_headers,
                                             sample_product):
        _fill_cart(client, admin_headers, sample_product)
        order_id = _create_order(client, admin_headers).get_json()['data']['order_id']
        assert client.post(_cancel_url(order_id),
                           headers=auth_headers).status_code in (403, 404)
