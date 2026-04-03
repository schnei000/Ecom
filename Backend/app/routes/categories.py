from flask import Blueprint, jsonify, request, current_app
from ..models import Product, Category
from ..extension import db, limiter
from ..utils.decorators import admin_required
from ..validators import sanitize_string, ValidationError
from ..utils.pagination import get_pagination_params

categories_bp = Blueprint('categories', __name__, url_prefix='/api/v1')


@categories_bp.route('/categories', methods=['GET'])
@limiter.limit("30 per minute")
def get_all_categories():
    """
    ---
    tags:
      - Catégories
    summary: Récupère une liste paginée de catégories.
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
        description: Une liste paginée de catégories.
      500:
        description: Erreur interne du serveur.
    """
    page, per_page = get_pagination_params(default_per_page=10)
    try:
        paginated = Category.query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in paginated.items],
            'pagination': {
                'total_categories': paginated.total,
                'total_pages': paginated.pages,
                'current_page': paginated.page,
                'per_page': paginated.per_page,
                'next_page': paginated.next_num,
                'prev_page': paginated.prev_num
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching categories: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la récupération des catégories'}), 500


@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    ---
    tags:
      - Catégories
    summary: Récupère les détails d'une catégorie spécifique par son ID.
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
        description: L'ID unique de la catégorie.
    responses:
      200:
        description: Détails de la catégorie.
      404:
        description: Catégorie non trouvée.
    """
    try:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Catégorie non trouvée'}), 404
        return jsonify({'success': True, 'data': category.to_dict()}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching category {category_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la récupération de la catégorie'}), 500


@categories_bp.route('/categories/<int:category_id>/products', methods=['GET'])
def get_products_by_category(category_id):
    """
    ---
    tags:
      - Catégories
    summary: Récupère une liste paginée de produits pour une catégorie spécifique.
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
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
        description: Une liste paginée de produits.
      404:
        description: Catégorie non trouvée.
    """
    page, per_page = get_pagination_params(default_per_page=10)
    try:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'success': False, 'message': 'Catégorie non trouvée'}), 404

        paginated = Product.query.filter_by(
            category_id=category.id, is_deleted=False
        ).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in paginated.items],
            'pagination': {
                'total_products': paginated.total,
                'total_pages': paginated.pages,
                'current_page': paginated.page,
                'per_page': paginated.per_page,
                'next_page': paginated.next_num,
                'prev_page': paginated.prev_num
            }
        }), 200
    except Exception as e:
        current_app.logger.error(
            f"Error fetching products for category {category_id}: {str(e)}", exc_info=True
        )
        return jsonify({'success': False, 'message': 'Erreur lors de la récupération des produits de la catégorie'}), 500


@categories_bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    """
    ---
    tags:
      - Catégories
    summary: Crée une nouvelle catégorie (Nécessite des droits administrateur).
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [name]
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Catégorie créée avec succès.
      409:
        description: Cette catégorie existe déjà.
    """
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'success': False, 'message': 'Le nom de la catégorie est requis'}), 400

        name = (data.get('name') or '').strip()
        description = (data.get('description') or '').strip()

        try:
            name = sanitize_string(name, max_length=120)
            if description:
                description = sanitize_string(description, max_length=2000)
        except ValidationError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        if Category.query.filter_by(name=name).first():
            return jsonify({'success': False, 'message': 'Cette catégorie existe déjà'}), 409

        new_category = Category(name=name, description=description or None)
        db.session.add(new_category)
        db.session.commit()
        current_app.logger.info(f"Category created: {name} (id={new_category.id}) by admin")

        return jsonify({
            'success': True,
            'data': new_category.to_dict(),
            'message': 'Catégorie créée avec succès'
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating category: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la création de la catégorie.'}), 500


@categories_bp.route('/categories/<int:category_id>', methods=['PUT', 'PATCH'])
@admin_required
def update_category(category_id):
    """
    ---
    tags:
      - Catégories
    summary: Met à jour une catégorie (Nécessite des droits administrateur).
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/Category'
    responses:
      200:
        description: Catégorie mise à jour avec succès.
      404:
        description: Catégorie non trouvée.
      409:
        description: Ce nom de catégorie est déjà utilisé.
    """
    try:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'success': False, 'message': 'Catégorie non trouvée'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Corps de la requête invalide.'}), 400

        if 'name' in data:
            name = (data.get('name') or '').strip()
            try:
                name = sanitize_string(name, max_length=120)
            except ValidationError as e:
                return jsonify({'success': False, 'message': str(e)}), 400

            if Category.query.filter(Category.id != category_id, Category.name == name).first():
                return jsonify({'success': False, 'message': 'Ce nom de catégorie est déjà utilisé'}), 409
            category.name = name

        if 'description' in data:
            description = (data.get('description') or '').strip()
            try:
                if description:
                    description = sanitize_string(description, max_length=2000)
                category.description = description or None
            except ValidationError as e:
                return jsonify({'success': False, 'message': str(e)}), 400

        db.session.commit()
        current_app.logger.info(f"Category updated: {category.name} (id={category_id}) by admin")

        return jsonify({
            'success': True,
            'data': category.to_dict(),
            'message': 'Catégorie mise à jour avec succès'
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating category {category_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour de la catégorie.'}), 500


@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """
    ---
    tags:
      - Catégories
    summary: Supprime une catégorie (Nécessite des droits administrateur).
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Catégorie supprimée avec succès.
      400:
        description: Impossible de supprimer, des produits sont associés à cette catégorie.
      404:
        description: Catégorie non trouvée.
    """
    try:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'success': False, 'message': 'Catégorie non trouvée'}), 404

        # Bloquer uniquement sur les produits actifs (non soft-deleted)
        active_products = [p for p in category.products if not p.is_deleted]
        if active_products:
            return jsonify({
                'success': False,
                'message': 'Impossible de supprimer, des produits actifs sont associés à cette catégorie.'
            }), 400

        db.session.delete(category)
        db.session.commit()
        current_app.logger.info(f"Category deleted: {category.name} (id={category_id}) by admin")

        return jsonify({'success': True, 'message': 'Catégorie supprimée avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting category {category_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la suppression de la catégorie.'}), 500
