from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt


def admin_required(fn):
    """Décorateur vérifiant que l'utilisateur est authentifié et possède les droits admin.
    Re-vérifie le statut admin en base de données pour éviter l'exploitation de tokens
    dont les claims seraient devenus obsolètes (ex : droits révoqués après émission).
    Retourne 403 avec un message standardisé si ce n'est pas le cas."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        # Vérification rapide via claims JWT (évite la DB si déjà refusé)
        if not claims.get("is_admin"):
            return jsonify({"success": False, "message": "Accès refusé. Droits administrateur requis."}), 403
        # Re-vérification en DB : s'assure que les droits n'ont pas été révoqués
        # depuis l'émission du token
        from ..extension import db
        from ..models import User
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user or user.is_deleted or not user.is_admin:
            return jsonify({"success": False, "message": "Accès refusé. Droits administrateur requis."}), 403
        return fn(*args, **kwargs)
    return wrapper