from flask import Blueprint, request, jsonify, current_app
from ..extension import db, bcrypt, limiter
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import timezone, datetime, timedelta
from ..models import User, TokenBlocklist
from ..validators import (
    validate_email, validate_username, validate_password, sanitize_string, ValidationError
)
from ..logging_config import log_security_event
from ..utils.email import send_reset_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth/v1")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    """
    ---
    tags:
      - Authentification
    summary: Enregistre un nouvel utilisateur avec validation robuste.
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
              description: Nom d'utilisateur (3-80 caractères, alphanumériques + underscore)
            email:
              type: string
              description: Adresse email valide
            password:
              type: string
              description: Mot de passe fort (8+ chars, uppercase, lowercase, digit, special char)
            nom:
              type: string
            prenom:
              type: string
    responses:
      201:
        description: Utilisateur enregistré avec succès.
      400:
        description: Données invalides ou manquantes.
      409:
        description: Utilisateur déjà existant.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Corps de la requête invalide."}), 400

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        nom = data.get("nom", "").strip()
        prenom = data.get("prenom", "").strip()

        if not all([username, email, password, nom, prenom]):
            return jsonify({"success": False, "message": "Tous les champs sont obligatoires."}), 400

        try:
            email = validate_email(email)
        except ValidationError as e:
            current_app.logger.warning(f"Registration failed: invalid email format - {email}")
            return jsonify({"success": False, "message": str(e)}), 400

        try:
            username = validate_username(username)
        except ValidationError as e:
            current_app.logger.warning(f"Registration failed: invalid username - {username}")
            return jsonify({"success": False, "message": str(e)}), 400

        try:
            validate_password(password)
        except ValidationError as e:
            current_app.logger.warning(f"Registration failed: weak password from {request.remote_addr}")
            return jsonify({"success": False, "message": str(e)}), 400

        try:
            nom = sanitize_string(nom, max_length=80)
            prenom = sanitize_string(prenom, max_length=80)
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e)}), 400

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            log_security_event(
                current_app.logger,
                'REGISTRATION_FAILED_DUPLICATE',
                reason='user_already_exists',
                identifier=email,
                ip=request.remote_addr
            )
            return jsonify({"success": False, "message": "Cet utilisateur existe déjà."}), 409

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            nom=nom,
            prenom=prenom,
            is_admin=False
        )

        db.session.add(new_user)
        db.session.commit()
        current_app.logger.info(f"User registered successfully: {username} ({email})")

        return jsonify({"success": True, "message": "Utilisateur enregistré avec succès."}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de l'enregistrement."}), 500


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """
    ---
    tags:
      - Authentification
    summary: Connecte un utilisateur et retourne les tokens JWT.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [password, email or username]
          properties:
            email:
              type: string
              description: Adresse email de l'utilisateur
            username:
              type: string
              description: Nom d'utilisateur
            password:
              type: string
              description: Mot de passe
    responses:
      200:
        description: Connexion réussie, tokens et informations utilisateur retournés.
      400:
        description: Données manquantes ou invalides.
      401:
        description: Identifiants incorrects.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Corps de la requête invalide."}), 400

        email_or_username = (data.get("email") or data.get("username") or "").strip()
        password = data.get("password", "")

        if not email_or_username or not password:
            return jsonify({"success": False, "message": "Email/utilisateur et mot de passe requis."}), 400

        # Exclure les comptes supprimés
        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username),
            User.is_deleted == False
        ).first()

        # Toujours exécuter bcrypt pour prévenir les timing attacks d'énumération de comptes
        dummy_hash = current_app.config.get('_TIMING_DUMMY_HASH', '')
        candidate_hash = user.password_hash if user else dummy_hash
        password_valid = bool(candidate_hash) and bcrypt.check_password_hash(candidate_hash, password)

        if not user:
            log_security_event(
                current_app.logger,
                'LOGIN_FAILED_USER_NOT_FOUND',
                identifier=email_or_username,
                ip=request.remote_addr
            )
            return jsonify({"success": False, "message": "Identifiants invalides."}), 401

        if not password_valid:
            log_security_event(
                current_app.logger,
                'LOGIN_FAILED_WRONG_PASSWORD',
                user_id=user.id,
                username=user.username,
                ip=request.remote_addr
            )
            return jsonify({"success": False, "message": "Identifiants invalides."}), 401

        if current_app.config.get('EMAIL_CONFIRMATION_REQUIRED') and not user.email_confirmed:
            return jsonify({"success": False, "message": "Veuillez confirmer votre adresse email avant de vous connecter."}), 403

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'is_admin': user.is_admin}
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        current_app.logger.info(f"User logged in: {user.username} from {request.remote_addr}")

        return jsonify({
            "success": True,
            "data": {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()),
                'user': user.to_dict()
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la connexion."}), 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@limiter.limit("10 per minute")
def refresh():
    """
    ---
    tags:
      - Authentification
    summary: Génère un nouveau token d'accès ET un nouveau refresh token (rotation).
    description: L'ancien refresh token est révoqué et un nouveau est émis à chaque appel.
    security:
      - Bearer: []
    responses:
      200:
        description: Nouveaux tokens générés.
      401:
        description: Refresh token invalide ou expiré.
    """
    try:
        user_id = int(get_jwt_identity())
        jwt_data = get_jwt()
        old_jti = jwt_data["jti"]
        now = datetime.now(timezone.utc)

        user = db.session.get(User, user_id)
        if not user or user.is_deleted:
            return jsonify({"success": False, "message": "Utilisateur non trouvé."}), 401

        # Rotation : révocation de l'ancien refresh token avant d'en émettre un nouveau
        exp_ts = jwt_data.get("exp")
        expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc) if exp_ts else (
            now + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
        )
        db.session.add(TokenBlocklist(jti=old_jti, created_at=now, expires_at=expires_at))

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'is_admin': user.is_admin}
        )
        new_refresh_token = create_refresh_token(identity=str(user.id))

        db.session.commit()
        current_app.logger.info(f"Token rotation for user: {user_id}")

        return jsonify({
            "success": True,
            "data": {
                'access_token': access_token,
                'refresh_token': new_refresh_token,
                'token_type': 'Bearer',
                'expires_in': int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors du renouvellement du token."}), 500


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def logout():
    """
    ---
    tags:
      - Authentification
    summary: Déconnecte l'utilisateur en révoquant le token JWT.
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            refresh_token:
              type: string
              description: Refresh token à révoquer (optionnel).
    responses:
      200:
        description: Déconnexion réussie.
      500:
        description: Erreur lors de la déconnexion.
    """
    try:
        user_id = int(get_jwt_identity())
        jwt_data = get_jwt()
        jti = jwt_data["jti"]
        now = datetime.now(timezone.utc)

        exp_ts = jwt_data.get("exp")
        expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc) if exp_ts else (
            now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )
        db.session.add(TokenBlocklist(jti=jti, created_at=now, expires_at=expires_at))

        # Révocation optionnelle du refresh token passé dans le body
        refresh_revoked = False
        data = request.get_json(silent=True) or {}
        refresh_token = data.get("refresh_token")
        if refresh_token:
            try:
                decoded = decode_token(refresh_token)
                token_type = decoded.get("type") or decoded.get("token_type")
                if token_type and token_type != "refresh":
                    current_app.logger.warning("Logout: non-refresh token fourni dans refresh_token")
                else:
                    refresh_jti = decoded.get("jti")
                    if refresh_jti:
                        ref_exp_ts = decoded.get("exp")
                        ref_expires_at = datetime.fromtimestamp(ref_exp_ts, tz=timezone.utc) if ref_exp_ts else (
                            now + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
                        )
                        db.session.add(TokenBlocklist(jti=refresh_jti, created_at=now, expires_at=ref_expires_at))
                        refresh_revoked = True
            except Exception as e:
                current_app.logger.warning(f"Refresh token invalide lors du logout: {str(e)}")

        db.session.commit()
        current_app.logger.info(f"User logged out: {user_id}")

        return jsonify({
            "success": True,
            "message": "Déconnexion réussie.",
            "refresh_revoked": refresh_revoked
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Logout error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la déconnexion."}), 500


@auth_bp.route("/request-reset", methods=["POST"])
@limiter.limit("3 per minute")
def request_password_reset():
    """
    ---
    tags:
      - Authentification
    summary: Demande un lien de réinitialisation de mot de passe par email.
    description: >
      Un email contenant un lien de réinitialisation (valable 15 minutes) est envoyé
      à l'adresse fournie si elle correspond à un compte actif.
      La réponse est identique qu'un compte existe ou non (anti-énumération).
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [email]
          properties:
            email:
              type: string
    responses:
      200:
        description: Email de réinitialisation envoyé (ou adresse inconnue, même réponse).
      500:
        description: Erreur lors de l'envoi de l'email.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Corps de la requête invalide."}), 400

        email = (data.get("email") or "").strip().lower()
        if not email:
            return jsonify({"success": False, "message": "L'email est requis."}), 400

        user = User.query.filter_by(email=email, is_deleted=False).first()
        # Réponse générique pour ne pas révéler l'existence d'un compte
        if not user:
            return jsonify({"success": True, "message": "Si cet email existe, un lien de réinitialisation a été envoyé."}), 200

        # pwd_sig lie le token au hash actuel : si le mot de passe change,
        # tous les anciens tokens de reset deviennent automatiquement invalides.
        pwd_sig = user.password_hash[-12:]
        reset_token = create_access_token(
            identity=str(user.id),
            additional_claims={'type': 'password_reset', 'pwd_sig': pwd_sig},
            expires_delta=timedelta(minutes=15)
        )

        try:
            send_reset_email(user.email, reset_token)
            current_app.logger.info(f"Password reset email sent for user: {user.id}")
        except EnvironmentError:
            # SMTP non configuré — log l'erreur sans bloquer (utile en développement local)
            current_app.logger.warning(
                f"SMTP non configuré : email de reset non envoyé pour user {user.id}. "
                "Définissez SMTP_HOST, SMTP_USER, SMTP_PASSWORD dans .env."
            )
        except Exception as e:
            current_app.logger.error(f"Erreur envoi email reset pour user {user.id}: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": "Erreur lors de l'envoi de l'email de réinitialisation."}), 500

        return jsonify({
            "success": True,
            "message": "Si cet email existe, un lien de réinitialisation a été envoyé."
        }), 200

    except Exception as e:
        current_app.logger.error(f"Password reset request error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la demande de réinitialisation."}), 500


@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password():
    """
    ---
    tags:
      - Authentification
    summary: Réinitialise le mot de passe avec un token valide.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [reset_token, new_password]
          properties:
            reset_token:
              type: string
              description: Token reçu par email via /auth/v1/request-reset
            new_password:
              type: string
              description: Nouveau mot de passe (8+ chars, majuscule, chiffre, caractère spécial)
    responses:
      200:
        description: Mot de passe réinitialisé avec succès.
      400:
        description: Token invalide, expiré ou mot de passe trop faible.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Corps de la requête invalide."}), 400

        reset_token = data.get("reset_token", "")
        new_password = data.get("new_password", "")

        if not reset_token or not new_password:
            return jsonify({"success": False, "message": "reset_token et new_password sont requis."}), 400

        try:
            decoded = decode_token(reset_token)
        except Exception:
            return jsonify({"success": False, "message": "Token invalide ou expiré."}), 400

        if decoded.get("type") != "password_reset":
            return jsonify({"success": False, "message": "Token invalide."}), 400

        # Vérifier que le token n'a pas déjà été consommé (usage unique)
        jti = decoded.get("jti")
        if jti and TokenBlocklist.query.filter_by(jti=jti).first():
            return jsonify({"success": False, "message": "Token déjà utilisé."}), 400

        user_id = decoded.get("sub")
        user = db.session.get(User, user_id)
        if not user or user.is_deleted:
            return jsonify({"success": False, "message": "Utilisateur non trouvé."}), 404

        # pwd_sig invalide si le mot de passe a déjà été changé depuis l'émission du token
        if decoded.get("pwd_sig") != user.password_hash[-12:]:
            return jsonify({"success": False, "message": "Token invalide ou déjà utilisé."}), 400

        try:
            validate_password(new_password)
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e)}), 400

        if jti:
            now = datetime.now(timezone.utc)
            exp_ts = decoded.get("exp")
            rt_expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc) if exp_ts else (
                now + timedelta(minutes=15)
            )
            db.session.add(TokenBlocklist(jti=jti, created_at=now, expires_at=rt_expires_at))

        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        current_app.logger.info(f"Password reset successful for user: {user.id}")

        return jsonify({"success": True, "message": "Mot de passe réinitialisé avec succès."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password reset error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la réinitialisation."}), 500
