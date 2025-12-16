from flask import Blueprint, request, jsonify
from ..admin import admin_bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Panier,Product
from ..extension import db

# creation Blueprint pou le panier

panier_bp = Blueprint('panier', __name__, url_prefix='/panier')

'''route pour ajouter un produit au panier'''
@panier_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_panier():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"message": "L'ID du produit ou la quantité est invalide."}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Le produit n'existe pas."}), 404

    # Vérification si le produit est déjà dans le panier
    item = Panier.query.filter_by(users_id=user_id, product_id=product_id).first()

    if item:
        # Si l'article existe, mettez à jour la quantité
        if product.stock < item.quantity + quantity:
            return jsonify({"message": "Stock insuffisant pour ajouter cette quantité."}), 400
        item.quantity += quantity
    else:
        # Sinon, créez un nouvel article dans le panier
        if product.stock < quantity:
            return jsonify({"message": "Stock insuffisant."}), 400
        new_item = Panier(users_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_item)

    db.session.commit()
    return jsonify({"message": "Produit ajouté au panier avec succès."}), 200

'''route pour voir le panier'''
@panier_bp.route('/view', methods=['GET'])
@jwt_required()
def view_panier():
    user_id = get_jwt_identity()
    panier_items = Panier.query.filter_by(users_id=user_id).all()
    return jsonify([item.to_dict() for item in panier_items])

'''pour modifier la quantite d'un produit dans le panier'''
@panier_bp.route('/update/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_panier(product_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    quantity = data.get('quantity')

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"message": "Quantité invalide."}), 400

    item = Panier.query.filter_by(users_id=user_id, product_id=product_id).first()
    if not item:
        return jsonify({"message": "Le produit n'est pas dans le panier."}), 404

    if item.product.stock < quantity:
        return jsonify({"message": "Stock insuffisant."}), 400

    item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "Quantité modifiée avec succès."})

'''pour supprimer un produit du panier'''
@panier_bp.route('/delete/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_from_panier(product_id):
    user_id = get_jwt_identity()
    item = Panier.query.filter_by(users_id=user_id, product_id=product_id).first()

    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Produit supprimé du panier."})
    else:
        return jsonify({"message": "Le produit n'est pas dans le panier."}), 404

'''pour vider le panier'''
@panier_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_panier():
    user_id = get_jwt_identity()
    Panier.query.filter_by(users_id=user_id).delete()
    db.session.commit()

    return jsonify({"message": "Le panier a été vidé."})