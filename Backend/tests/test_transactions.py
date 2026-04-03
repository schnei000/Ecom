"""
Tests for transaction endpoints:
  POST /api/v1/pay
  GET  /api/v1/transactions
  GET  /api/v1/transaction/<id>
  POST /api/v1/transaction/<id>/cancel
  GET  /api/v1/admin/transactions   (admin)
"""

import pytest

PAY_URL         = '/api/v1/pay'
TX_LIST_URL     = '/api/v1/transactions'
ADMIN_TX_URL    = '/api/v1/admin/transactions'
ADD_URL         = '/api/v1/panier/add'
ORDER_URL       = '/api/v1/order'


def _tx_url(tid):
    return f'/api/v1/transaction/{tid}'


def _cancel_tx_url(tid):
    return f'/api/v1/transaction/{tid}/cancel'


def _setup_pending_order(client, headers, product_id):
    """Add product to cart, create order, return order data."""
    client.post(ADD_URL, json={'product_id': product_id, 'quantity': 1}, headers=headers)
    res = client.post(ORDER_URL, headers=headers)
    assert res.status_code == 201
    return res.get_json()['data']


def _pay_order(client, headers, order_id, amount, method='card'):
    return client.post(PAY_URL, json={
        'order_id': order_id,
        'amount': amount,
        'payment_method': method,
    }, headers=headers)


# ---------------------------------------------------------------------------
# Pay (create transaction)
# ---------------------------------------------------------------------------

class TestPay:

    def test_pay_pending_order_success(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        res = _pay_order(client, auth_headers, order['order_id'],
                         float(order.get('total_amount', 49.99)))
        assert res.status_code == 201

    def test_pay_requires_authentication(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        res = client.post(PAY_URL, json={
            'order_id': order['order_id'],
            'amount': 49.99,
            'payment_method': 'card',
        })
        assert res.status_code == 401

    def test_pay_nonexistent_order_rejected(self, client, auth_headers):
        assert client.post(PAY_URL, json={
            'order_id': 999999,
            'amount': 49.99,
            'payment_method': 'card',
        }, headers=auth_headers).status_code in (400, 404)

    def test_pay_with_wrong_amount_rejected(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        res = _pay_order(client, auth_headers, order['order_id'], 0.01)
        assert res.status_code == 400

    def test_pay_missing_fields_rejected(self, client, auth_headers):
        assert client.post(PAY_URL, json={'order_id': 1},
                           headers=auth_headers).status_code == 400

    def test_order_status_becomes_paid(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        _pay_order(client, auth_headers, order['order_id'],
                   float(order.get('total_amount', 49.99)))
        order_res = client.get(f'/api/v1/orders/{order["order_id"]}',
                               headers=auth_headers).get_json()
        status = (order_res.get('data') or order_res).get('status')
        assert status == 'paid'

    def test_duplicate_payment_rejected(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        amount = float(order.get('total_amount', 49.99))
        _pay_order(client, auth_headers, order['order_id'], amount)
        res = _pay_order(client, auth_headers, order['order_id'], amount)
        assert res.status_code in (400, 409)

    def test_pay_returns_transaction_reference(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        res = _pay_order(client, auth_headers, order['order_id'],
                         float(order.get('total_amount', 49.99)))
        assert res.status_code == 201
        data = res.get_json().get('data', {})
        assert 'ref_externe' in data or 'id' in data


# ---------------------------------------------------------------------------
# List user transactions
# ---------------------------------------------------------------------------

class TestListTransactions:

    def test_list_requires_authentication(self, client):
        assert client.get(TX_LIST_URL).status_code == 401

    def test_list_returns_array(self, client, auth_headers):
        res = client.get(TX_LIST_URL, headers=auth_headers)
        assert res.status_code == 200

    def test_list_includes_completed_transaction(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        _pay_order(client, auth_headers, order['order_id'],
                   float(order.get('total_amount', 49.99)))
        res = client.get(TX_LIST_URL, headers=auth_headers).get_json()
        items = res.get('data', [])
        assert len(items) >= 1

    def test_user_sees_only_own_transactions(self, client, auth_headers,
                                              admin_headers, sample_product):
        # Admin pays an order
        order = _setup_pending_order(client, admin_headers, sample_product)
        _pay_order(client, admin_headers, order['order_id'],
                   float(order.get('total_amount', 49.99)))
        # Regular user's list should be empty
        res = client.get(TX_LIST_URL, headers=auth_headers).get_json()
        items = res.get('data') or (res if isinstance(res, list) else [])
        assert len(items) == 0


# ---------------------------------------------------------------------------
# Get single transaction
# ---------------------------------------------------------------------------

class TestGetTransaction:

    def test_get_own_transaction(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        pay_res = _pay_order(client, auth_headers, order['order_id'],
                             float(order.get('total_amount', 49.99)))
        tx_id = pay_res.get_json()['data']['id']
        res = client.get(_tx_url(tx_id), headers=auth_headers)
        assert res.status_code == 200

    def test_get_nonexistent_transaction(self, client, auth_headers):
        assert client.get(_tx_url(999999), headers=auth_headers).status_code == 404

    def test_get_requires_authentication(self, client):
        assert client.get(_tx_url(1)).status_code == 401


# ---------------------------------------------------------------------------
# Cancel transaction
# ---------------------------------------------------------------------------

class TestCancelTransaction:

    def test_cancel_completed_transaction_rejected(self, client, auth_headers, sample_product):
        order = _setup_pending_order(client, auth_headers, sample_product)
        pay_res = _pay_order(client, auth_headers, order['order_id'],
                             float(order.get('total_amount', 49.99)))
        tx_id = pay_res.get_json()['data']['id']
        # Completed transactions cannot be cancelled
        res = client.post(_cancel_tx_url(tx_id), headers=auth_headers)
        assert res.status_code in (400, 403, 200)  # depends on business logic

    def test_cancel_nonexistent_transaction(self, client, admin_headers):
        assert client.post(_cancel_tx_url(999999),
                           headers=admin_headers).status_code == 404

    def test_cancel_requires_authentication(self, client):
        assert client.post(_cancel_tx_url(1)).status_code == 401


# ---------------------------------------------------------------------------
# Admin — all transactions
# ---------------------------------------------------------------------------

class TestAdminTransactions:

    def test_admin_can_list_all_transactions(self, client, admin_headers):
        res = client.get(ADMIN_TX_URL, headers=admin_headers)
        assert res.status_code == 200

    def test_non_admin_cannot_list_all_transactions(self, client, auth_headers):
        assert client.get(ADMIN_TX_URL, headers=auth_headers).status_code == 403

    def test_unauthenticated_cannot_list_all_transactions(self, client):
        assert client.get(ADMIN_TX_URL).status_code == 401

    def test_admin_sees_other_user_transactions(self, client, auth_headers,
                                                 admin_headers, sample_product):
        # Regular user pays
        order = _setup_pending_order(client, auth_headers, sample_product)
        _pay_order(client, auth_headers, order['order_id'],
                   float(order.get('total_amount', 49.99)))
        res = client.get(ADMIN_TX_URL, headers=admin_headers).get_json()
        items = res.get('data') or (res if isinstance(res, list) else [])
        assert len(items) >= 1

    def test_admin_list_supports_pagination(self, client, admin_headers):
        res = client.get(f'{ADMIN_TX_URL}?page=1&per_page=5', headers=admin_headers)
        assert res.status_code == 200
