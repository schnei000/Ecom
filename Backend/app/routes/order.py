from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from ..extension import db
from ..models import Order, Panier, Product, OrderItem, Transaction

order_bp = Blueprint('order', __name__, url_prefix='/api/v1')


@order_bp.route('/order', methods=['POST'])
@jwt_required()
def create_order():
    """
    ---
    tags:
      - Commandes
    summary: Crée une commande à partir du panier de l'utilisateur.
    description: Valide le contenu du panier, vérifie les stocks, crée la commande et vide le panier.
    security:
      - Bearer: []
    responses:
      201:
        description: Commande créée avec succès.
      400:
        description: Panier vide ou stock insuffisant.
    """
    user_id = int(get_jwt_identity())
    cart_items = Panier.query.filter_by(user_id=user_id).all()

    existing_pending_order = Order.query.filter_by(user_id=user_id, status='pending').first()
    if existing_pending_order:
        current_app.logger.info(f"User {user_id} tried to create a second pending order (existing: {existing_pending_order.id})")
        return jsonify({
            "success": False,
            "message": "Vous avez déjà une commande en attente de paiement.",
            "data": {"order_id": existing_pending_order.id}
        }), 400

    if not cart_items:
        return jsonify({"success": False, "message": "Votre panier est vide."}), 400

    total_amount = 0
    order_items = []

    try:
        order = Order(user_id=user_id, total_amount=0)
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            product = db.session.query(Product).filter_by(id=item.product_id).with_for_update().first()

            if not product or product.is_deleted:
                raise ValueError(f"Le produit avec l'id {item.product_id} n'est plus disponible.")

            if product.stock < item.quantity:
                raise ValueError(f"Stock insuffisant pour le produit : {product.name}.")

            total_amount += float(product.price) * item.quantity
            product.stock -= item.quantity

            order_items.append(OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                unity_price=product.price
            ))

        order.total_amount = round(total_amount, 2)
        db.session.add_all(order_items)
        Panier.query.filter_by(user_id=user_id).delete()

        db.session.commit()
        current_app.logger.info(f"Order {order.id} created for user {user_id}, total={order.total_amount}")
        return jsonify({
            "success": True,
            "message": "Commande créée avec succès.",
            "data": {"order_id": order.id}
        }), 201

    except ValueError as e:
        db.session.rollback()
        current_app.logger.warning(f"Order creation failed for user {user_id}: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 400

    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"IntegrityError creating order for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur d'intégrité lors de la création de la commande."}), 409

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error creating order for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la création de la commande."}), 500


@order_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """
    ---
    tags:
      - Commandes
    summary: Récupère l'historique paginé des commandes de l'utilisateur.
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
        default: 10
    responses:
      200:
        description: Liste paginée des commandes.
    """
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    max_per_page = current_app.config.get('MAX_PER_PAGE', 100)
    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))

    paginated_orders = Order.query.filter_by(user_id=user_id).order_by(
        desc(Order.created_at)
    ).paginate(page=page, per_page=per_page, error_out=False)

    current_app.logger.info(f"User {user_id} fetched orders page {page}")
    return jsonify({
        "success": True,
        "data": [order.to_dict() for order in paginated_orders.items],
        "pagination": {
            'total_orders': paginated_orders.total,
            'total_pages': paginated_orders.pages,
            'current_page': paginated_orders.page,
            'per_page': paginated_orders.per_page,
        }
    }), 200


@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """
    ---
    tags:
      - Commandes
    summary: Récupère les détails d'une commande spécifique.
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Détails de la commande.
      404:
        description: Commande non trouvée.
    """
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).first()

    if not order:
        return jsonify({"success": False, "message": "Commande non trouvée."}), 404

    current_app.logger.info(f"User {user_id} fetched order {order_id}")
    return jsonify({"success": True, "data": order.to_dict(include_items=True)}), 200


@order_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """
    ---
    tags:
      - Commandes
    summary: Annule une commande en attente de paiement.
    description: Seules les commandes au statut 'pending' peuvent être annulées. Le stock est restitué.
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Commande annulée avec succès.
      400:
        description: La commande ne peut pas être annulée (déjà payée ou annulée).
      404:
        description: Commande non trouvée.
    """
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).first()

    if not order:
        return jsonify({"success": False, "message": "Commande non trouvée."}), 404

    if order.status == 'cancelled':
        return jsonify({"success": False, "message": "Cette commande est déjà annulée."}), 400

    if order.status == 'paid':
        return jsonify({"success": False, "message": "Impossible d'annuler une commande déjà payée. Contactez le support."}), 400

    try:
        # Restitution du stock pour chaque article
        for item in order.items:
            product = db.session.get(Product, item.product_id)
            if product:
                product.stock += item.quantity

        order.status = 'cancelled'

        # Annuler également toute transaction pending associée
        if order.transaction and order.transaction.status == 'pending':
            order.transaction.status = 'cancelled'

        db.session.commit()
        current_app.logger.info(f"Order {order_id} cancelled by user {user_id}")
        return jsonify({"success": True, "message": "Commande annulée avec succès.", "data": order.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling order {order_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de l'annulation de la commande."}), 500
