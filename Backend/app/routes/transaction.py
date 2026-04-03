from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from ..utils.decorators import admin_required
from ..extension import db
from ..models import Transaction, Order, OrderItem, Product, User
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
import uuid

transaction_bp = Blueprint('transaction', __name__, url_prefix='/api/v1')


@transaction_bp.route("/pay", methods=["POST"])
@jwt_required()
def create_transaction():
    """
    ---
    tags:
      - Transactions
    summary: Crée une transaction pour payer une commande.
    description: Crée une transaction, la lie à une commande et met à jour le statut de la commande à 'paid'.
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [order_id, amount]
          properties:
            order_id:
              type: integer
              description: L'ID de la commande à payer.
            amount:
              type: number
              format: float
              description: Le montant total de la transaction.
            payment_method:
              type: string
              description: "La méthode de paiement (ex: 'card')."
    responses:
      201:
        description: Transaction réussie.
      400:
        description: Données manquantes, montant incorrect ou commande déjà payée.
      404:
        description: Commande non trouvée.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Corps de la requête invalide."}), 400

        order_id = data.get("order_id")
        amount = data.get("amount")

        if order_id is None or amount is None:
            return jsonify({"success": False, "message": "order_id et amount sont requis."}), 400

        try:
            amount = round(float(amount), 2)
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "Le montant doit être un nombre valide."}), 400

        if amount < 0:
            return jsonify({"success": False, "message": "Le montant doit être positif."}), 400
        if amount > 999999.99:
            return jsonify({"success": False, "message": "Le montant dépasse la limite autorisée."}), 400

        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            return jsonify({"success": False, "message": "Commande non trouvée."}), 404

        if order.status == 'paid':
            return jsonify({"success": False, "message": "Cette commande a déjà été payée."}), 400
        if order.status == 'cancelled':
            return jsonify({"success": False, "message": "Cette commande est annulée."}), 400

        # Idempotence : vérifier qu'il n'existe pas déjà une transaction non-annulée pour cette commande
        existing_transaction = Transaction.query.filter(
            Transaction.order_id == order_id,
            Transaction.status != 'cancelled'
        ).first()
        if existing_transaction:
            return jsonify({
                "success": False,
                "message": "Une transaction existe déjà pour cette commande.",
                "data": existing_transaction.to_dict()
            }), 409

        order_amount = round(float(order.total_amount), 2)
        if order_amount != amount:
            return jsonify({"success": False, "message": "Le montant de la transaction ne correspond pas au montant total de la commande."}), 400

        # Création de la transaction avec statut 'pending' (défaut du modèle)
        transaction = Transaction(
            user_id=user_id,
            order_id=order_id,
            amount=order.total_amount,
            payment_method=data.get("payment_method", "card"),
            ref_externe=f"TXN-{uuid.uuid4().hex}"
        )
        db.session.add(transaction)
        db.session.flush()  # Obtenir l'ID sans committer

        # Simulation du traitement du paiement — en production : appel passerelle externe
        transaction.status = 'completed'
        order.status = 'paid'
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Transaction réussie.",
            "data": transaction.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Payment error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors du traitement du paiement."}), 500

@transaction_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    """
    ---
    tags:
      - Transactions
    summary: Récupère l'historique paginé des transactions de l'utilisateur.
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        description: Le numéro de la page à récupérer.
        default: 1
      - name: per_page
        in: query
        type: integer
        description: Le nombre de transactions par page.
        default: 10
    responses:
      200:
        description: Une liste paginée des transactions de l'utilisateur.
        schema:
          type: object
          properties:
            transactions:
              type: array
              items:
                $ref: '#/definitions/Transaction'
            pagination:
              type: object
    """
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    max_per_page = current_app.config.get('MAX_PER_PAGE', 100)
    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))

    paginated_transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    transactions_list = [tx.to_dict() for tx in paginated_transactions.items]

    return jsonify({
        "success": True,
        "data": transactions_list,
        "pagination": {
            'total_transactions': paginated_transactions.total,
            'total_pages': paginated_transactions.pages,
            'current_page': paginated_transactions.page,
            'per_page': paginated_transactions.per_page
        }
    }), 200

@transaction_bp.route("/transaction/<int:transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction(transaction_id):
    """
    ---
    tags:
      - Transactions
    summary: Récupère les détails d'une transaction spécifique.
    security:
      - Bearer: []
    parameters:
      - name: transaction_id
        in: path
        type: integer
        required: true
        description: L'ID de la transaction.
    responses:
      200:
        description: Détails de la transaction.
        schema:
          $ref: '#/definitions/Transaction'
      404:
        description: Transaction non trouvée.
    """
    user_id = int(get_jwt_identity())
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()

    if not transaction:
        return jsonify({"success": False, "message": "Transaction non trouvée."}), 404

    return jsonify({"success": True, "data": transaction.to_dict()}), 200

@transaction_bp.route("/transaction/<int:transaction_id>/cancel", methods=["POST"])
@admin_required
def cancel_transaction(transaction_id):
    """
    ---
    tags:
      - Transactions
    summary: Annule une transaction (Admin requis).
    security:
      - Bearer: []
    parameters:
      - name: transaction_id
        in: path
        type: integer
        required: true
        description: L'ID de la transaction à annuler.
    responses:
      200:
        description: Transaction annulée avec succès.
      400:
        description: La transaction est déjà annulée.
      404:
        description: Transaction non trouvée.
    """
    admin_id = int(get_jwt_identity())

    transaction = Transaction.query.filter_by(id=transaction_id).first()

    if not transaction:
        return jsonify({"success": False, "message": "Transaction non trouvée."}), 404

    if transaction.status == 'cancelled':
        return jsonify({"success": False, "message": "La transaction est déjà annulée."}), 400

    current_app.logger.warning(
        f"ADMIN_ACTION: cancel_transaction | admin_id={admin_id} | transaction_id={transaction_id} | user_id={transaction.user_id}"
    )
    transaction.status = 'cancelled'
    order = Order.query.filter_by(id=transaction.order_id).first()
    if order:
        # Si la commande n'était pas déjà annulée, on restitue le stock
        if order.status != 'cancelled':
            for item in order.items:
                product = db.session.get(Product, item.product_id)
                if product:
                    product.stock += item.quantity
        order.status = 'cancelled'

    try:
        db.session.commit()
        current_app.logger.info(f"Transaction {transaction_id} cancelled by admin {admin_id}")
        return jsonify({"success": True, "message": "Transaction annulée avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling transaction {transaction_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de l'annulation de la transaction."}), 500

@transaction_bp.route("/admin/transactions", methods=["GET"])
@admin_required
def get_all_transactions_admin():
    """
    ---
    tags:
      - Transactions
    summary: Liste toutes les transactions avec détail commande et produits (Admin requis).
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
    responses:
      200:
        description: Liste paginée des transactions avec détails.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    max_per_page = current_app.config.get('MAX_PER_PAGE', 100)
    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))

    paginated = (
        Transaction.query
        .options(
            joinedload(Transaction.order).joinedload(Order.items).joinedload(OrderItem.product),
        )
        .order_by(Transaction.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    result = []
    for tx in paginated.items:
        user = db.session.get(User, tx.user_id)
        items = []
        if tx.order:
            for item in tx.order.items:
                items.append({
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else 'Produit supprimé',
                    'quantity': item.quantity,
                    'unity_price': float(item.unity_price) if item.unity_price else 0,
                })
        result.append({
            'id': tx.id,
            'ref_externe': tx.ref_externe,
            'amount': float(tx.amount) if tx.amount else 0,
            'status': tx.status,
            'payment_method': tx.payment_method,
            'created_at': tx.created_at.isoformat() if tx.created_at else None,
            'user': {
                'id': user.id if user else tx.user_id,
                'username': user.username if user else '—',
                'email': user.email if user else '—',
            },
            'order_id': tx.order_id,
            'items': items,
        })

    return jsonify({
        'success': True,
        'data': result,
        'pagination': {
            'total': paginated.total,
            'total_pages': paginated.pages,
            'current_page': paginated.page,
            'per_page': paginated.per_page,
        }
    }), 200


@transaction_bp.route("/transactions/daily", methods=["GET"])
@admin_required
def get_daily_transactions():
    """
    ---
    tags:
      - Transactions
    summary: Obtenir un rapport journalier des transactions (Admin requis).
    description: Retourne le nombre total de transactions et le montant total pour chaque jour.
    security:
      - Bearer: []
    responses:
      200:
        description: Rapport des transactions journalières.
      403:
        description: Accès refusé. Droits administrateur requis.
    """
    current_app.logger.warning(
        f"ADMIN_ACTION: get_daily_transactions | admin_id={get_jwt_identity()}"
    )
    # Exclure les transactions annulées du rapport journalier
    daily_transactions = db.session.query(
        func.date(Transaction.created_at).label('date'),
        func.count(Transaction.id).label('total_transactions'),
        func.sum(Transaction.amount).label('total_amount')
    ).filter(Transaction.status != 'cancelled').group_by(func.date(Transaction.created_at)).all()

    result = []
    for dt in daily_transactions:
        result.append({
            "date": dt.date,
            "total_transactions": dt.total_transactions,
            "total_amount": float(dt.total_amount) if dt.total_amount else 0.0
        })

    return jsonify({"success": True, "data": result}), 200
