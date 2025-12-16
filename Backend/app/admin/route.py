from flask import jsonify
from flask_jwt_extended import jwt_required
from . import admin_bp
from ..utils.decorators import admin_required

'''Routes pour les opérations administratives'''
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard():
    return jsonify({"message": "Welcome to the admin dashboard!"}), 200