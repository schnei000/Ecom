from flask import Blueprint, request, jsonify
from ..extension import db, bcrypt, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Route Register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    nom = data.get("nom")
    prenom = data.get("prenom")

# validons les donnees 
    if not all([username, email, password, nom,prenom]):
        return jsonify({"message": "Tout les champs sont obligatoires."}), 400
    '''verifions si l'utilisateur existe deja'''
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"message": "Nom d'utilisateur ou email deja utilise."}), 409
    '''hashons le mot de passe'''
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    '''creons un nouvel utilisateur'''
    new_user = User(
        username= username,
        email= email,
        password= hashed_password,
        nom= nom,
        prenom= prenom

    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Utilisateur enregistre avec succes."}), 201


# Route Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email_or_username = data.get("email") or data.get("username")
    password = data.get("password")

    '''validation des donnees'''
    if not all([email_or_username, password]):
        return jsonify({"message": "Tout les champs sont obligatoires."}), 400
    
    '''verifions si l'utilisateur existe'''
    user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Email/nom d'utilisateur ou mot de passe incorrect."}), 401
    
    '''creons le token d'acces'''
    acces_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(hours=3)
       
    )
    return jsonify({
        'access_token': acces_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'nom': user.nom,
            'prenom': user.prenom,
            'is_admin': user.is_admin
        }
    })