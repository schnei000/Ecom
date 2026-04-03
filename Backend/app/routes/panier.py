from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from ..models import Panier, Product
from ..extension import db, limiter
from ..validators import validate_quantity, ValidationError

panier_bp = Blueprint('panier', __name__, url_prefix='/api/v1/panier')

@panier_bp.route('/add', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
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
              description: La quantité à ajouter (1-10000).
    responses:
      200:
        description: Produit ajouté au panier avec succès.
      400:
        description: Données invalides ou stock insuffisant.
      404:
        description: Produit non trouvé.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "Corps de la requête invalide."}), 400
        
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        if not product_id:
            return jsonify({"success": False, "message": "L'ID du produit est requis."}), 400
        
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "L'ID du produit doit être un entier."}), 400
        
        try:
            quantity = validate_quantity(quantity, max_quantity=10000)
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e)}), 400
        
        # Check product exists — verrou FOR UPDATE pour lecture atomique du stock
        product = db.session.query(Product).filter_by(id=product_id, is_deleted=False).with_for_update().first()
        if not product:
            return jsonify({"success": False, "message": "Le produit n'existe pas."}), 404

        if product.stock < quantity:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "Stock insuffisant."
            }), 400
        
        item = Panier.query.filter_by(user_id=user_id, product_id=product_id).first()
        
        if item:
            # Vérification combinée sur le même objet verrouillé
            if product.stock < (item.quantity + quantity):
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": f"Stock insuffisant. Vous avez déjà {item.quantity} unité(s) dans le panier."
                }), 400
            item.quantity += quantity
        else:
            item = Panier(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(item)
        
        db.session.commit()
        current_app.logger.info(f"User {user_id} added {quantity} x product {product_id} to cart")
        
        return jsonify({
            "success": True,
            "message": "Produit ajouté au panier avec succès.",
            "data": item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding to panier: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de l'ajout au panier."}), 500


@panier_bp.route('/view', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def view_panier():
    """
    ---
    tags:
      - Panier
    summary: Affiche le contenu du panier de l'utilisateur (paginé).
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
        default: 50
    responses:
      200:
        description: Contenu du panier.
    """
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        max_per_page = current_app.config.get('MAX_PER_PAGE', 100)
        page = max(1, page)
        per_page = max(1, min(per_page, max_per_page))

        paginated = Panier.query.filter_by(user_id=user_id).options(
            joinedload(Panier.product)
        ).paginate(page=page, per_page=per_page, error_out=False)

        # Total calculé sur TOUT le panier via SQL (pas seulement la page courante)
        total_price = db.session.query(
            func.sum(Product.price * Panier.quantity)
        ).select_from(Panier).join(Product, Panier.product_id == Product.id).filter(
            Panier.user_id == user_id,
            Product.is_deleted == False
        ).scalar() or 0

        return jsonify({
            "success": True,
            "data": [item.to_dict() for item in paginated.items],
            "total_items": paginated.total,
            "total_price": round(float(total_price), 2),
            "pagination": {
                "current_page": paginated.page,
                "total_pages": paginated.pages,
                "per_page": paginated.per_page
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error viewing panier: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la lecture du panier."}), 500


@panier_bp.route('/update/<int:product_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("20 per minute")
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
              description: La nouvelle quantité (0 pour supprimer, 1-10000 pour mettre à jour).
    responses:
      200:
        description: Quantité modifiée avec succès.
      400:
        description: Quantité invalide ou stock insuffisant.
      404:
        description: Le produit n'est pas dans le panier.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "Corps de la requête invalide."}), 400
        
        quantity = data.get('quantity')
        
        # quantity=0 supprime l'article du panier
        try:
            if quantity == 0:
                item = Panier.query.filter_by(user_id=user_id, product_id=product_id).first()
                if not item:
                    return jsonify({"success": False, "message": "Le produit n'est pas dans le panier."}), 404
                db.session.delete(item)
                db.session.commit()
                current_app.logger.info(f"User {user_id} removed product {product_id} from cart")
                return jsonify({"success": True, "message": "Produit supprimé du panier."}), 200
            else:
                quantity = validate_quantity(quantity, max_quantity=10000)
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e)}), 400
        
        item = Panier.query.filter_by(user_id=user_id, product_id=product_id).first()
        if not item:
            return jsonify({"success": False, "message": "Le produit n'est pas dans le panier."}), 404

        # Verrou FOR UPDATE pour lecture atomique du stock
        product = db.session.query(Product).filter_by(id=product_id, is_deleted=False).with_for_update().first()
        if not product or product.stock < quantity:
            return jsonify({
                "success": False,
                "message": f"Stock insuffisant. Stock disponible: {product.stock if product else 0}"
            }), 400
        
        item.quantity = quantity
        db.session.commit()
        current_app.logger.info(f"User {user_id} updated quantity of product {product_id} to {quantity}")
        
        return jsonify({
            "success": True, 
            "message": "Quantité modifiée avec succès.",
            "data": item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating panier: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la mise à jour du panier."}), 500


@panier_bp.route('/delete/<int:product_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("20 per minute")
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
    try:
        user_id = int(get_jwt_identity())
        item = Panier.query.filter_by(user_id=user_id, product_id=product_id).first()
        
        if not item:
            return jsonify({"success": False, "message": "Le produit n'est pas dans le panier."}), 404
        
        db.session.delete(item)
        db.session.commit()
        current_app.logger.info(f"User {user_id} removed product {product_id} from cart")
        
        return jsonify({"success": True, "message": "Produit supprimé du panier."}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting from panier: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la suppression."}), 500


@panier_bp.route('/clear', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")
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
    try:
        user_id = int(get_jwt_identity())
        Panier.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        current_app.logger.info(f"User {user_id} cleared their cart")
        
        return jsonify({"success": True, "message": "Le panier a été vidé."}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error clearing panier: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors du vidage du panier."}), 500
