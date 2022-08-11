from flask import Blueprint
from controllers.show import create_show_submission, create_shows, shows

show_bp = Blueprint('show_bp', __name__)

show_bp.get('/')(shows)
show_bp.get('/create')(create_shows)
show_bp.post('/create')(create_show_submission)
