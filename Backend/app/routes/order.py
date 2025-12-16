from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from ..extension import db
from ..models import Order, Panier, Product, OrderItem

# Creation Blueprint pour order
order_bp = Blueprint('order',__name__)

'''Ajouter un produit au panier'''
@order_bp.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or not quantity:
        return jsonify({"message": "product_id et quantity sont requis"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Produit non trouvé"}), 404

    if product.stock < quantity:
        return jsonify({"message": "Stock insuffisant"}), 400

    # Vérifier si le produit est déjà dans le panier
    cart_item = Panier.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        # Mettre à jour la quantité
        cart_item.quantity += quantity
    else:
        # Ajouter un nouvel article au panier
        cart_item = Panier(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Produit ajouté au panier avec succès"}), 201

'''Création de la commande à partir du panier'''
@order_bp.route('/order', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    cart_items = Panier.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return jsonify({"message": "Votre panier est vide"}), 400

    total_amount = 0
    order_items = []

    try:
        # Créer la commande
        order = Order(user_id=user_id, total_amount=0) # Montant total mis à jour après
        db.session.add(order)
        db.session.flush() # Pour obtenir l'ID de la commande avant le commit

        for item in cart_items:
            product = Product.query.get(item.product_id)
            if not product:
                 raise Exception(f"Produit avec id {item.product_id} non trouvé.")

            if product.stock < item.quantity:
                raise Exception(f"Stock insuffisant pour le produit: {product.name}")

            total_amount += product.price * item.quantity
            product.stock -= item.quantity

            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=item.quantity, price=product.price)
            order_items.append(order_item)

        order.total_amount = total_amount
        db.session.add_all(order_items)

        # Vider le panier de l'utilisateur
        Panier.query.filter_by(user_id=user_id).delete()

        db.session.commit()
        return jsonify({"message": "Commande créée avec succès", "order_id": order.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400
