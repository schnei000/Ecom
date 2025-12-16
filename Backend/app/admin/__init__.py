from flask import Blueprint

'''initialisation du Blueprint pour l'administration'''

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

from . import route  
from . import categorie
from . import product