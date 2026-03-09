from flask import Blueprint, jsonify, request
from ..models import Product, Category
from ..extension import db
from ..utils.decorators import admin_required

# Blueprint public pour les produits et catégories
products_bp = Blueprint('products', __name__, url_prefix='/api')

# ========== PRODUITS ==========

@products_bp.route('/products', methods=['GET'])
def get_all_products():
    """
    ---
    tags:
      - Produits
    summary: Récupère une liste paginée de produits.
    parameters:
      - name: page
        in: query
        type: integer
        description: Le numéro de la page à récupérer.
        default: 1
      - name: per_page
        in: query
        type: integer
        description: Le nombre de produits par page.
        default: 10
    responses:
      200:
        description: Une liste paginée de produits.
      500:
        description: Erreur interne du serveur.
    """
    # Récupérer les arguments de pagination de l'URL, avec des valeurs par défaut
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        # Utiliser la méthode paginate() de SQLAlchemy au lieu de .all()
        paginated_products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
        products_list = [product.to_dict() for product in paginated_products.items]

        return jsonify({
            'success': True,
            'data': products_list,
            'pagination': {
                'total_products': paginated_products.total,
                'total_pages': paginated_products.pages,
                'current_page': paginated_products.page,
                'per_page': paginated_products.per_page,
                'next_page': paginated_products.next_num,
                'prev_page': paginated_products.prev_num
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des produits'
        }), 500


@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    ---
    tags:
      - Produits
    summary: Récupère les détails d'un produit spécifique par son ID.
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: L'ID unique du produit.
    responses:
      200:
        description: Détails du produit.
      404:
        description: Produit non trouvé.
    """
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': 'NOT_FOUND',
                'message': 'Produit non trouvé'
            }), 404
        
        return jsonify({
            'success': True,
            'data': product.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération du produit'
        }), 500

@products_bp.route('/products', methods=['POST'])
@admin_required
def create_product():
    """
    ---
    tags:
      - Produits
    summary: Crée un nouveau produit (Nécessite des droits administrateur).
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
            - category_id
          properties:
            name:
              type: string
              description: Nom du produit.
            description:
              type: string
              description: Description détaillée du produit.
            price:
              type: number
              format: float
              description: Prix du produit.
            stock:
              type: integer
              description: Quantité en stock.
            category_id:
              type: integer
              description: ID de la catégorie associée.
    responses:
      201:
        description: Produit créé avec succès.
      400:
        description: Données d'entrée invalides ou manquantes.
      403:
        description: Droits administrateur requis.
      409:
        description: Un produit avec ce nom existe déjà.
    """
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    category_id = data.get("category_id")
    stock = data.get("stock")

    # Validation des données plus robuste (inspirée de admin/product.py)
    if not all([name, price is not None, category_id is not None]):
        return jsonify({
            'success': False,
            'message': "Le nom, le prix et l'ID de la catégorie sont obligatoires."
        }), 400

    if (isinstance(price, (int, float)) and price < 0) or (stock is not None and isinstance(stock, int) and stock < 0):
        return jsonify({'success': False, 'message': "La valeur du prix ou du stock est invalide."}), 400

    if not Category.query.get(category_id):
        return jsonify({'success': False, 'message': "Catégorie non trouvée."}), 404

    if Product.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': "Un produit avec ce nom existe déjà."}), 409

    try:
        new_product = Product(
            name=name,
            description=data.get('description'),
            price=price,
            stock=stock,
            category_id=category_id
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': new_product.to_dict(),
            'message': 'Produit créé avec succès'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la création du produit'
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT', 'PATCH'])
@admin_required
def update_product(product_id):
    """
    ---
    tags:
      - Produits
    summary: Met à jour un produit existant (Nécessite des droits administrateur).
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/Product'
    responses:
      200:
        description: Produit mis à jour avec succès.
      403:
        description: Droits administrateur requis.
      404:
        description: Produit non trouvé.
      409:
        description: Un autre produit avec ce nom existe déjà.
    """
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()

        name = data.get("name")
        if name and name != product.name:
            if Product.query.filter(Product.name == name, Product.id != product_id).first():
                return jsonify({"success": False, "message": "Un autre produit avec ce nom existe déjà."}), 409
            product.name = name

        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.stock = data.get('stock', product.stock)
        product.category_id = data.get('category_id', product.category_id)

        db.session.commit()

        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': 'Produit mis à jour avec succès'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la mise à jour du produit'
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """
    ---
    tags:
      - Produits
    summary: Supprime un produit (Nécessite des droits administrateur).
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Produit supprimé avec succès.
      403:
        description: Droits administrateur requis.
      404:
        description: Produit non trouvé.
    """
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Produit supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 'message': 'Erreur lors de la suppression du produit'
        }), 500


# ========== CATÉGORIES ==========

@products_bp.route('/categories', methods=['GET'])
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
        description: Le numéro de la page à récupérer.
        default: 1
      - name: per_page
        in: query
        type: integer
        description: Le nombre de catégories par page.
        default: 10
    responses:
      200:
        description: Une liste paginée de catégories.
      500:
        description: Erreur interne du serveur.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        paginated_categories = Category.query.paginate(page=page, per_page=per_page, error_out=False)
        categories_list = [categorie.to_dict() for categorie in paginated_categories.items]
        return jsonify({
            'success': True,
            'data': categories_list,
            'pagination': {
                'total_categories': paginated_categories.total,
                'total_pages': paginated_categories.pages,
                'current_page': paginated_categories.page,
                'per_page': paginated_categories.per_page,
                'next_page': paginated_categories.next_num,
                'prev_page': paginated_categories.prev_num
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des catégories'
        }), 500


@products_bp.route('/categories/<int:category_id>', methods=['GET'])
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
        category = Category.query.get(category_id)
        if not category:
            return jsonify({
                'success': False,
                'error': 'NOT_FOUND',
                'message': 'Catégorie non trouvée'
            }), 404
        
        return jsonify({
            'success': True,
            'data': category.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération de la catégorie'
        }), 500

@products_bp.route('/categories/<int:category_id>/products', methods=['GET'])
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
        description: L'ID de la catégorie.
      - name: page
        in: query
        type: integer
        description: Le numéro de la page à récupérer.
        default: 1
      - name: per_page
        in: query
        type: integer
        description: Le nombre de produits par page.
        default: 10
    responses:
      200:
        description: Une liste paginée de produits.
      404:
        description: Catégorie non trouvée.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        # On s'assure que la catégorie existe avant de requêter les produits
        category = Category.query.get_or_404(category_id)
        paginated_products = Product.query.filter_by(category_id=category.id).paginate(page=page, per_page=per_page, error_out=False)
        products_list = [product.to_dict() for product in paginated_products.items]

        return jsonify({
            'success': True,
            'data': products_list,
            'pagination': {'total_products': paginated_products.total, 'total_pages': paginated_products.pages, 'current_page': paginated_products.page, 'per_page': paginated_products.per_page, 'next_page': paginated_products.next_num, 'prev_page': paginated_products.prev_num}
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des produits de la catégorie'
        }), 500

@products_bp.route('/categories', methods=['POST'])
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
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': 'Le nom de la catégorie est requis'}), 400

    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'success': False, 'message': 'Cette catégorie existe déjà'}), 409

    try:
        new_category = Category(name=data['name'], description=data.get('description'))
        db.session.add(new_category)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': new_category.to_dict(),
            'message': 'Catégorie créée avec succès'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/categories/<int:category_id>', methods=['PUT', 'PATCH'])
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
        category = Category.query.get_or_404(category_id)
        data = request.get_json()

        if 'name' in data and Category.query.filter(Category.id != category_id, Category.name == data['name']).first():
            return jsonify({'success': False, 'message': 'Ce nom de catégorie est déjà utilisé'}), 409

        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': category.to_dict(),
            'message': 'Catégorie mise à jour avec succès'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/categories/<int:category_id>', methods=['DELETE'])
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
        category = Category.query.get_or_404(category_id)
        if category.products:
            return jsonify({'success': False, 'message': 'Impossible de supprimer, des produits sont associés à cette catégorie'}), 400
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Catégorie supprimée avec succès'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
