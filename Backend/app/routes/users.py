from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import timezone, datetime
from ..extension import db, bcrypt, limiter
from ..models import User, TokenBlocklist
from ..utils.decorators import admin_required
from ..utils.pagination import get_pagination_params
from ..validators import validate_email, validate_username, validate_password, sanitize_string, ValidationError
from ..logging_config import log_security_event

users_bp = Blueprint("users", __name__, url_prefix="/auth/v1")


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    ---
    tags:
      - Utilisateurs
    summary: Retourne les informations de l'utilisateur connecté.
    security:
      - Bearer: []
    responses:
      200:
        description: Informations utilisateur.
      401:
        description: Non authentifié.
    """
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)

        if not user or user.is_deleted:
            return jsonify({"success": False, "message": "Utilisateur non trouvé."}), 401

        return jsonify({"success": True, "data": user.to_dict()}), 200

    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la récupération des informations."}), 500


@users_bp.route("/me/delete", methods=["POST"])
@jwt_required()
def delete_account():
    """
    ---
    tags:
      - Utilisateurs
    summary: Supprime le compte de l'utilisateur connecté (soft delete).
    description: >
      Désactive le compte de manière irréversible côté utilisateur.
      Les données sont conservées en base (soft delete) pour la cohérence des commandes.
      Le token actif est révoqué immédiatement.
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [password]
          properties:
            password:
              type: string
              description: Mot de passe actuel pour confirmer la suppression.
    responses:
      200:
        description: Compte supprimé avec succès.
      400:
        description: Mot de passe manquant ou incorrect.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True) or {}
        password = data.get("password", "")

        if not password:
            return jsonify({"success": False, "message": "Le mot de passe est requis pour confirmer la suppression."}), 400

        user = db.session.get(User, user_id)
        if not user or user.is_deleted:
            return jsonify({"success": False, "message": "Utilisateur non trouvé."}), 404

        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"success": False, "message": "Mot de passe incorrect."}), 400

        # Soft delete + révocation immédiate du token courant
        user.is_deleted = True
        jwt_data = get_jwt()
        jti = jwt_data["jti"]
        now = datetime.now(timezone.utc)
        exp_ts = jwt_data.get("exp")
        expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc) if exp_ts else (
            now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )
        db.session.add(TokenBlocklist(jti=jti, created_at=now, expires_at=expires_at))
        db.session.commit()

        current_app.logger.info(f"Account deleted (soft) for user: {user_id}")
        return jsonify({"success": True, "message": "Compte supprimé avec succès."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete account error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la suppression du compte."}), 500


@users_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    """
    ---
    tags:
      - Utilisateurs
    summary: Liste tous les utilisateurs (Admin requis).
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
        default: 20
    responses:
      200:
        description: Liste paginée des utilisateurs.
    """
    page, per_page = get_pagination_params(default_per_page=20)

    paginated = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    current_app.logger.info(f"Admin fetched users list (page {page})")
    return jsonify({
        "success": True,
        "data": [u.to_dict() for u in paginated.items],
        "pagination": {
            "total": paginated.total,
            "total_pages": paginated.pages,
            "current_page": paginated.page,
            "per_page": paginated.per_page,
        }
    }), 200


@users_bp.route("/me", methods=["PUT", "PATCH"])
@jwt_required()
@limiter.limit("10 per minute")
def update_profile():
    """Update current user's profile fields (prenom, nom, username, email)."""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)

        if not user or user.is_deleted:
            return jsonify({"success": False, "message": "Utilisateur non trouvé."}), 404

        data = request.get_json(silent=True) or {}

        updated = False

        # prenom
        if "prenom" in data:
            prenom = data["prenom"].strip()
            if prenom:
                try:
                    user.prenom = sanitize_string(prenom, max_length=80)
                    updated = True
                except ValidationError as e:
                    return jsonify({"success": False, "message": str(e)}), 400

        # nom
        if "nom" in data:
            nom = data["nom"].strip()
            if nom:
                try:
                    user.nom = sanitize_string(nom, max_length=80)
                    updated = True
                except ValidationError as e:
                    return jsonify({"success": False, "message": str(e)}), 400

        # username
        if "username" in data:
            username = data["username"].strip()
            if username:
                try:
                    username = validate_username(username)
                except ValidationError as e:
                    return jsonify({"success": False, "message": str(e)}), 400

                conflict = User.query.filter(
                    User.username == username,
                    User.id != user_id,
                    User.is_deleted == False
                ).first()
                if conflict:
                    return jsonify({"success": False, "message": "Ce nom d'utilisateur est déjà pris."}), 409

                user.username = username
                updated = True

        # email
        if "email" in data:
            email = data["email"].strip()
            if email:
                try:
                    email = validate_email(email)
                except ValidationError as e:
                    return jsonify({"success": False, "message": str(e)}), 400

                conflict = User.query.filter(
                    User.email == email,
                    User.id != user_id,
                    User.is_deleted == False
                ).first()
                if conflict:
                    return jsonify({"success": False, "message": "Cette adresse email est déjà utilisée."}), 409

                user.email = email
                updated = True

        if not updated:
            return jsonify({"success": False, "message": "Aucun champ valide fourni."}), 400

        db.session.commit()
        current_app.logger.info(f"Profile updated for user {user_id}")
        return jsonify({"success": True, "message": "Profil mis à jour.", "data": user.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update profile error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la mise à jour."}), 500


@users_bp.route("/me/password", methods=["PATCH"])
@jwt_required()
@limiter.limit("5 per minute")
def change_password():
    """Change current user's password. Requires current password for verification."""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)

        if not user or user.is_deleted:
            return jsonify({"success": False, "message": "Utilisateur non trouvé."}), 404

        data = request.get_json(silent=True) or {}
        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")

        if not current_password or not new_password:
            return jsonify({"success": False, "message": "Mot de passe actuel et nouveau mot de passe requis."}), 400

        if not bcrypt.check_password_hash(user.password_hash, current_password):
            log_security_event(
                current_app.logger,
                'PASSWORD_CHANGE_FAILED_WRONG_CURRENT',
                user_id=user_id,
                ip=request.remote_addr
            )
            return jsonify({"success": False, "message": "Mot de passe actuel incorrect."}), 400

        try:
            validate_password(new_password)
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e)}), 400

        if bcrypt.check_password_hash(user.password_hash, new_password):
            return jsonify({"success": False, "message": "Le nouveau mot de passe doit être différent de l'ancien."}), 400

        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        current_app.logger.info(f"Password changed for user {user_id}")
        return jsonify({"success": True, "message": "Mot de passe mis à jour avec succès."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Change password error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors du changement de mot de passe."}), 500
