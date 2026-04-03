from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity
from ..models import Product, Category
from ..extension import db, limiter
from ..utils.decorators import admin_required
from ..validators import validate_price, validate_stock, sanitize_string, ValidationError
from ..utils.uploads import delete_product_image, parse_bool, save_product_image
from ..utils.pagination import get_pagination_params

products_bp = Blueprint('products', __name__, url_prefix='/api/v1')


def _get_request_payload():
    if request.content_type and 'multipart/form-data' in request.content_type:
        return request.form.to_dict()
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _parse_category_id(raw_value):
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        raise ValidationError("L'ID de la catégorie doit être un entier valide.")


@products_bp.route('/products', methods=['GET'])
@limiter.limit("60 per minute")
def get_all_products():
    """
    ---
    tags:
      - Produits
    summary: Récupère une liste paginée de produits avec filtres optionnels.
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 10
      - name: search
        in: query
        type: string
        description: Recherche dans le nom et la description.
      - name: min_price
        in: query
        type: number
        description: Prix minimum.
      - name: max_price
        in: query
        type: number
        description: Prix maximum.
      - name: in_stock
        in: query
        type: boolean
        description: Si true, retourne uniquement les produits en stock.
      - name: category_id
        in: query
        type: integer
        description: Filtre par catégorie.
    responses:
      200:
        description: Une liste paginée de produits.
      500:
        description: Erreur interne du serveur.
    """
    page, per_page = get_pagination_params(default_per_page=10)

    search = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    if min_price is not None and min_price < 0:
        return jsonify({'success': False, 'message': 'min_price ne peut pas être négatif.'}), 400
    if max_price is not None and max_price < 0:
        return jsonify({'success': False, 'message': 'max_price ne peut pas être négatif.'}), 400
    if min_price is not None and max_price is not None and min_price > max_price:
        return jsonify({'success': False, 'message': 'min_price ne peut pas être supérieur à max_price.'}), 400

    in_stock = request.args.get('in_stock', '').lower() in ('true', '1', 'yes')
    category_id = request.args.get('category_id', type=int)

    try:
        query = Product.query.filter_by(is_deleted=False)

        if search:
            # Échapper les wildcards SQL pour éviter une recherche non intentionnelle
            escaped = search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            like = f"%{escaped}%"
            query = query.filter(
                db.or_(Product.name.ilike(like), Product.description.ilike(like))
            )
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if in_stock:
            query = query.filter(Product.stock > 0)
        if category_id:
            query = query.filter_by(category_id=category_id)

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

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
        current_app.logger.error(f"Error fetching products: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la récupération des produits'}), 500


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
        product = Product.query.filter_by(id=product_id, is_deleted=False).first()
        if not product:
            return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Produit non trouvé'}), 404
        return jsonify({'success': True, 'data': product.to_dict()}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching product {product_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la récupération du produit'}), 500


@products_bp.route('/uploads/products/<path:filename>', methods=['GET'])
@limiter.limit("600 per minute")
def get_product_image(filename):
    if '/' in filename or '\\' in filename:
        return jsonify({'success': False, 'message': 'Nom de fichier invalide.'}), 400
    upload_dir = current_app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']
    return send_from_directory(upload_dir, filename, conditional=True)


@products_bp.route('/products', methods=['POST'])
@admin_required
@limiter.limit("20 per minute")
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
              description: Nom du produit (1-120 caractères).
            description:
              type: string
              description: Description détaillée du produit.
            price:
              type: number
              format: float
              description: Prix du produit (0.00 à 999999.99).
            stock:
              type: integer
              description: Quantité en stock (0 à 1000000).
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
    saved_image_filename = None

    try:
        data = _get_request_payload()
        if not data:
            return jsonify({'success': False, 'message': "Corps de la requête invalide."}), 400

        name = (data.get("name") or "").strip()
        description = (data.get("description") or "").strip()
        price = data.get("price")
        stock = data.get("stock", 0)
        category_id = data.get("category_id")
        image_file = request.files.get('image')

        if not all([name, price is not None, category_id is not None]):
            return jsonify({'success': False, 'message': "Le nom, le prix et l'ID de la catégorie sont obligatoires."}), 400

        try:
            name = sanitize_string(name, max_length=120)
        except ValidationError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        try:
            price = validate_price(price)
        except ValidationError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        try:
            stock = validate_stock(stock)
        except ValidationError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        try:
            category_id = _parse_category_id(category_id)
        except ValidationError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        try:
            if description:
                description = sanitize_string(description, max_length=2000)
        except ValidationError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'success': False, 'message': "Catégorie non trouvée."}), 404

        # Exclure les produits supprimés du contrôle d'unicité du nom
        if Product.query.filter_by(name=name, is_deleted=False).first():
            return jsonify({'success': False, 'message': "Un produit avec ce nom existe déjà."}), 409

        if image_file and image_file.filename:
            try:
                saved_image_filename = save_product_image(image_file)
            except ValidationError as e:
                return jsonify({'success': False, 'message': str(e)}), 400

        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            image_filename=saved_image_filename
        )

        db.session.add(new_product)
        db.session.commit()
        current_app.logger.info(f"Product created: {name} (id={new_product.id}) by admin")

        return jsonify({
            'success': True,
            'data': new_product.to_dict(),
            'message': 'Produit créé avec succès'
        }), 201

    except Exception as e:
        db.session.rollback()
        if saved_image_filename:
            delete_product_image(saved_image_filename)
        current_app.logger.error(f"Error creating product: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la création du produit'}), 500


@products_bp.route('/products/<int:product_id>', methods=['PUT', 'PATCH'])
@admin_required
@limiter.limit("20 per minute")
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
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
            category_id:
              type: integer
    responses:
      200:
        description: Produit mis à jour avec succès.
      400:
        description: Données invalides.
      403:
        description: Droits administrateur requis.
      404:
        description: Produit non trouvé.
      409:
        description: Un autre produit avec ce nom existe déjà.
    """
    saved_image_filename = None
    old_image_filename = None
    should_delete_old_image = False
    should_delete_current_image = False

    try:
        product = Product.query.filter_by(id=product_id, is_deleted=False).first()
        if not product:
            return jsonify({"success": False, "message": "Produit non trouvé."}), 404

        data = _get_request_payload()
        if not data:
            return jsonify({'success': False, 'message': "Corps de la requête invalide."}), 400

        image_file = request.files.get('image')
        remove_image = parse_bool(data.get('remove_image'))

        if 'name' in data:
            name = (data.get('name') or "").strip()
            if name:
                try:
                    name = sanitize_string(name, max_length=120)
                    if name != product.name:
                        existing = Product.query.filter(
                            Product.name == name,
                            Product.id != product_id,
                            Product.is_deleted == False
                        ).first()
                        if existing:
                            return jsonify({"success": False, "message": "Un autre produit avec ce nom existe déjà."}), 409
                    product.name = name
                except ValidationError as e:
                    return jsonify({'success': False, 'message': str(e)}), 400

        if 'price' in data and data['price'] is not None:
            try:
                product.price = validate_price(data['price'])
            except ValidationError as e:
                return jsonify({'success': False, 'message': str(e)}), 400

        if 'stock' in data and data['stock'] is not None:
            try:
                product.stock = validate_stock(data['stock'])
            except ValidationError as e:
                return jsonify({'success': False, 'message': str(e)}), 400

        if 'description' in data:
            description = (data.get('description') or "").strip()
            try:
                if description:
                    description = sanitize_string(description, max_length=2000)
                product.description = description
            except ValidationError as e:
                return jsonify({'success': False, 'message': str(e)}), 400

        if 'category_id' in data:
            category_id = data.get('category_id')
            if category_id:
                try:
                    category_id = _parse_category_id(category_id)
                except ValidationError as e:
                    return jsonify({'success': False, 'message': str(e)}), 400

                category = db.session.get(Category, category_id)
                if not category:
                    return jsonify({'success': False, 'message': "Catégorie non trouvée."}), 404
                product.category_id = category_id

        if image_file and image_file.filename:
            try:
                saved_image_filename = save_product_image(image_file)
            except ValidationError as e:
                return jsonify({'success': False, 'message': str(e)}), 400

            old_image_filename = product.image_filename
            product.image_filename = saved_image_filename
            should_delete_old_image = bool(old_image_filename)
        elif remove_image and product.image_filename:
            old_image_filename = product.image_filename
            product.image_filename = None
            should_delete_current_image = True

        db.session.commit()

        if should_delete_old_image and old_image_filename:
            delete_product_image(old_image_filename)
        if should_delete_current_image and old_image_filename:
            delete_product_image(old_image_filename)

        current_app.logger.info(f"Product updated: {product.name} (id={product_id}) by admin")

        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': 'Produit mis à jour avec succès'
        }), 200

    except Exception as e:
        db.session.rollback()
        if saved_image_filename:
            delete_product_image(saved_image_filename)
        current_app.logger.error(f"Error updating product {product_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour du produit'}), 500


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
@limiter.limit("10 per minute")
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
        product = Product.query.filter_by(id=product_id, is_deleted=False).first()
        if not product:
            return jsonify({"success": False, "message": "Produit non trouvé."}), 404

        # Soft delete : on marque le produit comme supprimé sans le retirer de la DB
        # Les commandes existantes gardent ainsi leur référence au produit
        product.is_deleted = True
        db.session.commit()

        current_app.logger.info(f"Product soft-deleted: {product.name} (id={product_id}) by admin")

        return jsonify({'success': True, 'message': 'Produit supprimé avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting product {product_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erreur lors de la suppression du produit'}), 500


@products_bp.route('/products/<int:product_id>/stock', methods=['PATCH'])
@admin_required
def adjust_stock(product_id):
    """
    ---
    tags:
      - Produits
    summary: Ajuste le stock d'un produit (Admin requis).
    description: >
      Permet un ajustement relatif (delta positif ou négatif) ou absolu du stock.
      Utilisez 'delta' pour ajouter/retirer des unités, ou 'absolute' pour fixer une valeur exacte.
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
          type: object
          properties:
            delta:
              type: integer
              description: "Variation relative (ex: +10 pour réappro, -3 pour correction)"
            absolute:
              type: integer
              description: "Valeur absolue du nouveau stock (prioritaire sur delta)"
    responses:
      200:
        description: Stock mis à jour avec succès.
      400:
        description: Données invalides ou stock résultant négatif.
      404:
        description: Produit non trouvé.
    """
    admin_id = get_jwt_identity()

    product = db.session.get(Product, product_id)
    if not product or product.is_deleted:
        return jsonify({'success': False, 'message': 'Produit non trouvé.'}), 404

    data = request.get_json(silent=True) or {}

    if 'absolute' in data:
        try:
            new_stock = int(data['absolute'])
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'La valeur de stock doit être un entier.'}), 400
        if new_stock < 0:
            return jsonify({'success': False, 'message': 'Le stock ne peut pas être négatif.'}), 400
        old_stock = product.stock
        product.stock = new_stock
    elif 'delta' in data:
        try:
            delta = int(data['delta'])
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Le delta doit être un entier.'}), 400
        new_stock = product.stock + delta
        if new_stock < 0:
            return jsonify({'success': False, 'message': f'Stock insuffisant. Stock actuel : {product.stock}, delta : {delta}.'}), 400
        old_stock = product.stock
        product.stock = new_stock
    else:
        return jsonify({'success': False, 'message': "Fournissez 'delta' ou 'absolute'."}), 400

    try:
        db.session.commit()
        current_app.logger.warning(
            f"ADMIN_ACTION: adjust_stock | admin_id={admin_id} | product_id={product_id} "
            f"| old_stock={old_stock} | new_stock={product.stock}"
        )
        return jsonify({
            'success': True,
            'message': 'Stock mis à jour avec succès.',
            'data': {'product_id': product_id, 'old_stock': old_stock, 'new_stock': product.stock}
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adjusting stock for product {product_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': "Erreur lors de la mise à jour du stock."}), 500
