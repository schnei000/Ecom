from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from ..utils.decorators import admin_required
from ..extension import db
from ..models import Transaction, User, Order, OrderItem, Product
from datetime import datetime

# creation du Blueprint pour la Transaction
transaction_bp = Blueprint('transaction', __name__, url_prefix='/api')

'''Route pour creer une transaction'''
@transaction_bp.route("/pay", methods=["POST"])
@jwt_required()
def create_transaction():
    user_id = get_jwt_identity()
    data = request.get_json()
    order_id = data.get("order_id")
    amount = data.get("amount")

    if order_id is None or amount is None:
        return jsonify({"message": "order_id et amount sont requis."}), 400
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({"message": "Le montant doit être un nombre valide."}), 400
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"message": "Commande non trouvée."}), 404

    '''Vérifions si la commande n'est pas déjà payée'''
    if order.status == 'paid':
        return jsonify({"message": "Cette commande a déjà été payée."}), 400
    
    '''Vérification du montant'''
    if order.total_amount != amount:
        return jsonify({"message": "Le montant de la transaction ne correspond pas au montant total de la commande."}), 400
    
    '''Création de la transaction'''
    transaction = Transaction(
        user_id = user_id,
        order_id = order_id,
        amount = order.total_amount,
        status ="completed",
        ref_externe = f"SIM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{user_id}"
    )
    db.session.add(transaction)
    order.status = 'paid'
    db.session.commit()

    transaction_data = {
        "id": transaction.id,
        "order_id": transaction.order_id,
        "amount": transaction.amount,
        "status": transaction.status,
        "ref_externe": transaction.ref_externe
    }

    return jsonify({"message": "Transaction reussie.", "transaction": transaction_data}), 201

''' Route pour voir l'historique des transactions'''
@transaction_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=user_id).all()

    transactions_list = [{
        "id": tx.id,
        "order_id": tx.order_id,
        "amount": tx.amount,
        "status": tx.status,
        "ref_externe": tx.ref_externe,
        "created_at": tx.created_at
    } for tx in transactions]

    return jsonify({"transactions": transactions_list}), 200

''' Route pour voir les details d'une transaction'''
@transaction_bp.route("/transaction/<int:transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction(transaction_id):
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()

    if not transaction:
        return jsonify({"message": "Transaction non trouvée."}), 404

    transaction_data = {
        "id": transaction.id,
        "order_id": transaction.order_id,
        "amount": transaction.amount,
        "status": transaction.status,
        "ref_externe": transaction.ref_externe,
        "created_at": transaction.created_at
    }

    return jsonify({"transaction": transaction_data}), 200

'''pour annuler une transaction'''
@transaction_bp.route("/transaction/<int:transaction_id>/cancel", methods=["POST"])
@jwt_required()
@admin_required
def cancel_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id).first()

    if not transaction:
        return jsonify({"message": "Transaction non trouvée."}), 404

    if transaction.status == 'cancelled':
        return jsonify({"message": "La transaction est deja annulee."}), 400

    transaction.status = 'cancelled'
    order = Order.query.filter_by(id=transaction.order_id).first()
    if order:
        order.status = 'cancelled'

    db.session.commit()

    return jsonify({"message": "Transaction annulee avec succes."}), 200

''' Route pour vois les transaction journalieres (admin seulement)'''
@transaction_bp.route("/transactions/daily", methods=["GET"])
@jwt_required()
@admin_required
def get_daily_transactions():
    from sqlalchemy import func
    daily_transactions = db.session.query(
        func.date(Transaction.created_at).label('date'),
        func.count(Transaction.id).label('total_transactions'),
        func.sum(Transaction.amount).label('total_amount')
    ).group_by(func.date(Transaction.created_at)).all()

    result = []
    for dt in daily_transactions:
        result.append({
            "date": dt.date,
            "total_transactions": dt.total_transactions,
            "total_amount": float(dt.total_amount)
        })

    return jsonify({"daily_transactions": result}), 200