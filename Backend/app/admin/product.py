from flask import request, jsonify
from . import admin_bp
from ..utils.decorators import admin_required
from ..extension import db
from flask_jwt_extended import jwt_required
from ..models import Product, Categorie

'''Routes pour creer un Produit'''
@admin_bp.route('/products', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    stock = data.get("stock")
    categorie_id = data.get("categorie_id")

    '''validation des données'''
    if not name or price is None or not categorie_id:
        return jsonify({"message": "Le nom, le prix et l'ID de la catégorie sont obligatoires."}), 400

    if (isinstance(price, (int, float)) and price < 0) or (stock is not None and isinstance(stock, int) and stock < 0):
        return jsonify({'message': "La valeur du prix ou du stock est invalide."}), 400

    categorie = Categorie.query.get(categorie_id)
    if not categorie:
        return jsonify({"message": "Catégorie non trouvée."}), 404

    existing_product = Product.query.filter_by(name=name).first()
    if existing_product:
        return jsonify({"message": "Un produit avec ce nom existe déjà."}), 409

    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        categorie_id=categorie_id
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Produit créé avec succès.", "product": product.to_dict()}), 201

'''Route pour récupérer tous les produits'''
@admin_bp.route('/products', methods=['GET'])
@jwt_required()
@admin_required
def get_products():
    products = Product.query.all()
    product_list = [product.to_dict() for product in products]
    return jsonify(product_list), 200

'''Route pour récupérer un produit par son id'''
@admin_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

'''Route pour mettre à jour un produit'''
@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    name = data.get("name")
    if name and name != product.name:
        existing_product = Product.query.filter(Product.name == name, Product.id != product_id).first()
        if existing_product:
            return jsonify({"message": "Un autre produit avec ce nom existe déjà."}), 409
        product.name = name

    product.description = data.get("description", product.description)
    product.price = data.get("price", product.price)
    product.stock = data.get("stock", product.stock)
    product.categorie_id = data.get("categorie_id", product.categorie_id)

    db.session.commit()
    return jsonify({"message": "Produit mis à jour avec succès.", "product": product.to_dict()}), 200

'''Route pour supprimer un produit'''
@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Produit supprimé avec succès."}), 200