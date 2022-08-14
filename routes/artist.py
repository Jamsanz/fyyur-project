from flask import Blueprint

from controllers.artist import artists, create_artist_form, create_artist_submission, delete_artist, edit_artist_submission, search_artists, show_artist

artist_bp = Blueprint('artist_bp', __name__)

artist_bp.get('/')(artists)
artist_bp.get('/<int:artist_id>')(show_artist)
artist_bp.get('/create')(create_artist_form)
artist_bp.post('/create')(create_artist_submission)
artist_bp.post('/search')(search_artists)
artist_bp.get('/<int:artist_id>/edit')(edit_artist_submission)
artist_bp.post('/<int:artist_id>/edit')(edit_artist_submission)
artist_bp.delete('/<int:artist_id>')(delete_artist)
