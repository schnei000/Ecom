from flask import Blueprint, request, jsonify
from app.extension import db, bcrypt, jwt
from app.models import User
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
    return jsonify({"message": "Login endpoint"}), 200


