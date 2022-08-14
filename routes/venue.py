from crypt import methods
from flask import Blueprint

from controllers.venue import create_venue_form, create_venue_submission, delete_venue, edit_venue, edit_venue_submission, search_venues, show_venue, venues

venue_bp = Blueprint('venue_bp', __name__ )

venue_bp.get('')(venues)
venue_bp.get('/<int:venue_id>')(show_venue)
venue_bp.get('/create')(create_venue_form)
venue_bp.post('/create')(create_venue_submission)
venue_bp.post('/search')(search_venues)
venue_bp.get('/<int:venue_id>/edit')(edit_venue)
venue_bp.post('/<int:venue_id>/edit')(edit_venue_submission)
venue_bp.delete('/<int:venue_id>')(delete_venue)
