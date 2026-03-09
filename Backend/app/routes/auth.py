from flask import Blueprint, request, jsonify
from ..extension import db, bcrypt, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from ..models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Route Register
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    ---
    tags:
      - Authentification
    summary: Enregistre un nouvel utilisateur.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [username, email, password, nom, prenom]
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            nom:
              type: string
            prenom:
              type: string
    responses:
      201:
        description: Utilisateur enregistré avec succès.
      400:
        description: Données manquantes.
      409:
        description: Nom d'utilisateur ou email déjà utilisé.
    """
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    nom = data.get("nom")
    prenom = data.get("prenom")

# validons les donnees 
    if not all([username, email, password, nom,prenom]):
        return jsonify({"message": "Tout les champs sont obligatoires."}), 400
    # verifions si l'utilisateur existe deja
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"message": "Nom d'utilisateur ou email deja utilise."}), 409
    # hashons le mot de passe
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # creons un nouvel utilisateur
    new_user = User(
        username= username,
        email= email,
        password_hash= hashed_password,
        nom= nom,
        prenom= prenom

    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Utilisateur enregistre avec succes."}), 201


# Route Login
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    ---
    tags:
      - Authentification
    summary: Connecte un utilisateur et retourne un token JWT.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [password]
          properties:
            email:
              type: string
              description: Email ou nom d'utilisateur.
            username:
              type: string
              description: Email ou nom d'utilisateur.
            password:
              type: string
    responses:
      200:
        description: Connexion réussie, token et informations utilisateur retournés.
      400:
        description: Données manquantes.
      401:
        description: Identifiants incorrects.
    """
    data = request.get_json()
    email_or_username = data.get("email") or data.get("username")
    password = data.get("password")

    # validation des donnees
    if not all([email_or_username, password]):
        return jsonify({"message": "Tout les champs sont obligatoires."}), 400
    
    # verifions si l'utilisateur existe
    user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Email/nom d'utilisateur ou mot de passe incorrect."}), 401
    
    # creons le token d'acces
    acces_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(hours=3),
        additional_claims={'is_admin': user.is_admin}
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