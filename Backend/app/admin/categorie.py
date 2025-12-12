from flask import Blueprint, request, jsonify
from app.admin import admin_bp
from flask_jwt_extended import jwt_required
from app.models import Categorie
from app.utils.decorators import admin_required
from app.extension import db

'''Routes pour la gestion des catégories'''
@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
@admin_required
def create_categorie():
    data = request.get_json()
    nom = data.get("nom")
    description = data.get("description")

    '''validation des données'''
    if not nom:
        return jsonify({"message": "Le nom de la catégorie est obligatoire."}), 409
    
    existing_categorie = Categorie.query.filter_by(nom=nom).first()
    if existing_categorie:
        return jsonify({"message": "Une catégorie avec ce nom existe déjà."}), 409
    
    '''création de la nouvelle catégorie'''
    new_categorie = Categorie(
        id=None,
        nom=nom,
        description=description
    )
    db.session.add(new_categorie)
    db.session.commit()

    return jsonify(
        {
            "message": "Catégorie créée avec succès.",
            "categorie": new_categorie.to_dict()
        }
    ), 201   

'''Route pour récupérer toutes les catégories'''
@admin_bp.route("/categories", methods=['GET'])
@jwt_required()
@admin_required
def get_categories():
    categories = Categorie.query.all()
    categorie_list = [categorie.to_dict() for categorie in categories]

    return jsonify(categorie_list), 200

'''Route pour récupérer une catégorie par son nom'''
@admin_bp.route("/categories/<nom>", methods=['GET'])
@jwt_required()
@admin_required
def get_categorie_by_nom(nom):
    categorie = Categorie.query.filter_by(nom=nom).first_or_404(description=f"Catégorie '{nom}' non trouvée.")
    return jsonify(categorie.to_dict()), 200

'''Route pour mettre à jour une catégorie'''
@admin_bp.route("/categories/<int:categorie_id>", methods=['PUT'])
@jwt_required()
@admin_required
def update_categorie(categorie_id):
    categorie = Categorie.query.get_or_404(categorie_id)
    data = request.get_json()
    nom = data.get("nom")
    description = data.get("description")

    if not nom:
        return jsonify({"message": "Le nom de la catégorie est obligatoire."}), 409
    
    # Vérifier si un autre catégorie avec le même nom existe déjà
    existing_categorie = Categorie.query.filter(Categorie.nom == nom, Categorie.id != categorie_id).first()
    if existing_categorie:
        return jsonify({"message": "Une catégorie avec ce nom existe déjà."}), 409
    
    categorie.nom = nom
    categorie.description = description
    db.session.commit()

    return jsonify({
        "message": "Catégorie mise à jour avec succès.",
        "categorie": categorie.to_dict()
    }), 200

'''Route pour supprimer une catégorie'''
@admin_bp.route("/categories/<int:categorie_id>", methods=['DELETE'])
@jwt_required()
@admin_required
def delete_categorie(categorie_id):
    categorie = Categorie.query.get_or_404(categorie_id)
    db.session.delete(categorie)
    db.session.commit()
    return jsonify({"message": "Catégorie supprimée avec succès."}), 200
    
