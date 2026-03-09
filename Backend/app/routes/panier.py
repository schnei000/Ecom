from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Panier,Product
from ..extension import db

# creation Blueprint pou le panier

panier_bp = Blueprint('panier', __name__, url_prefix='/api/panier')

# route pour ajouter un produit au panier
@panier_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_panier():
    """
    ---
    tags:
      - Panier
    summary: Ajoute un produit au panier de l'utilisateur.
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [product_id, quantity]
          properties:
            product_id:
              type: integer
              description: L'ID du produit à ajouter.
            quantity:
              type: integer
              description: La quantité à ajouter.
    responses:
      200:
        description: Produit ajouté au panier avec succès.
      400:
        description: Données invalides ou stock insuffisant.
      404:
        description: Produit non trouvé.
    """
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
    item = Panier.query.filter_by(user_id=user_id, product_id=product_id).first()

    if item:
        # Si l'article existe, mettez à jour la quantité
        if product.stock < item.quantity + quantity:
            return jsonify({"message": "Stock insuffisant pour ajouter cette quantité."}), 400
        item.quantity += quantity
    else:
        # Sinon, créez un nouvel article dans le panier
        if product.stock < quantity:
            return jsonify({"message": "Stock insuffisant."}), 400
        new_item = Panier(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_item)

    db.session.commit()
    return jsonify({"message": "Produit ajouté au panier avec succès."}), 200

# route pour voir le panier
@panier_bp.route('/view', methods=['GET'])
@jwt_required()
def view_panier():
    """
    ---
    tags:
      - Panier
    summary: Affiche le contenu du panier de l'utilisateur.
    security:
      - Bearer: []
    responses:
      200:
        description: Contenu du panier.
        schema:
          type: array
          items:
            $ref: '#/definitions/Panier'
    """
    user_id = get_jwt_identity()
    panier_items = Panier.query.filter_by(user_id=user_id).all()
    return jsonify([item.to_dict() for item in panier_items])

# pour modifier la quantite d'un produit dans le panier
@panier_bp.route('/update/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_panier(product_id):
    """
    ---
    tags:
      - Panier
    summary: Met à jour la quantité d'un produit dans le panier.
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: L'ID du produit à mettre à jour.
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [quantity]
          properties:
            quantity:
              type: integer
              description: La nouvelle quantité.
    responses:
      200:
        description: Quantité modifiée avec succès.
      400:
        description: Quantité invalide ou stock insuffisant.
      404:
        description: Le produit n'est pas dans le panier.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    quantity = data.get('quantity')

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"message": "Quantité invalide."}), 400

    item = Panier.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return jsonify({"message": "Le produit n'est pas dans le panier."}), 404

    if item.product.stock < quantity:
        return jsonify({"message": "Stock insuffisant."}), 400

    item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "Quantité modifiée avec succès."}), 200

# pour supprimer un produit du panier
@panier_bp.route('/delete/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_from_panier(product_id):
    """
    ---
    tags:
      - Panier
    summary: Supprime un produit du panier.
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: L'ID du produit à supprimer.
    responses:
      200:
        description: Produit supprimé du panier.
      404:
        description: Le produit n'est pas dans le panier.
    """
    user_id = get_jwt_identity()
    item = Panier.query.filter_by(user_id=user_id, product_id=product_id).first()

    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Produit supprimé du panier."})
    else:
        return jsonify({"message": "Le produit n'est pas dans le panier."}), 404

# pour vider le panier
@panier_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_panier():
    """
    ---
    tags:
      - Panier
    summary: Vide complètement le panier de l'utilisateur.
    security:
      - Bearer: []
    responses:
      200:
        description: Le panier a été vidé.
    """
    user_id = get_jwt_identity()
    Panier.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({"message": "Le panier a été vidé."}), 200