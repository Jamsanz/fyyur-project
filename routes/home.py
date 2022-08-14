from crypt import methods
from flask import Blueprint
from controllers.home import index

home_bp = Blueprint('home_bp', __name__)

home_bp.route('')(index)