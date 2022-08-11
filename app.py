#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
from email.policy import default
import json
import sys
from typing import Final
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:7909@localhost:5432/fyyur'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500), nullable=True )
    shows = db.relationship('Show', backref='venue', lazy=True)

    def serialize(self):
      return {
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'genres': self.genres,
        'seeking_talent': self.seeking_talent
      }
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120), nullable = True)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  error = False
  search_term = request.form.get('search_term')
  try:
    results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    data = []
    for artist in results:
      res = {
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': len(artist.shows)
      }
      data.append(res)
    response = {
      'count': len(data),
      'data': data
    }
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error = False
  past_shows = []
  upcoming_shows = []
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()
    for show in venue.shows:
      if datetime.now() > show.start_time:
        artist = Artist.query.filter(Artist.id == show.artist_id).first()
        past_show = {
          'artist_id': show,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time.strftime('%Y-%m-%d %H:%I')
        }
        past_shows.append(past_show)
      else:
        artist = Artist.query.filter(Artist.id == show.artist_id).first()
        upcoming_show = {
          'artist_id': show,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time.strftime('%Y-%m-%d %H:%I')
        }
        upcoming_shows.append(upcoming_show)
    venue.upcoming_shows = upcoming_shows
    venue.upcoming_shows_count = len(upcoming_shows)
    venue.past_shows = past_shows
    venue.past_shows_count = len(past_shows)
    venue.genres = venue.genres
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('pages/show_venue.html', venue=venue)

    
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
  seeking_description = request.form.get('seeking_description')
  try:
    venue = Venue(
      name=name, 
      city=city, 
      state=state,
      address=address,
      phone=phone,
      genres=genres, 
      facebook_link=facebook_link, 
      image_link=image_link, 
      website_link=website_link, 
      seeking_talent=seeking_talent, 
      seeking_description=seeking_description
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('Oops! an error occurred')
      abort(400)
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('Oops! an error occurred')
      abort(400)
    else:
      return redirect(url_for('home'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.with_entities(Artist.id, Artist.name).all();
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  error = False
  search_term = request.form.get('search_term')
  try:
    results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = []
    for artist in results:
      res = {
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': len(artist.shows)
      }
      data.append(res)
    response = {
      'count': len(data),
      'data': data
    }
    print(response)
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  error = False
  upcoming_shows = []
  past_shows = []
  try:
    artist = Artist.query.filter(Artist.id==artist_id).first()
    for show in artist.shows:
      if datetime.now() > show.start_time:
        venue = Venue.query.filter(Venue.id == show.venue_id).first()
        upcoming_show = {
          'venue_id': show.venue_id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time.strftime('%Y-%m-%d %H:%I')
        }
        upcoming_shows.append(upcoming_show)
      else:
        venue = Venue.query.filter(Venue.id == show.venue_id).first()
        past_show = {
          'venue_id': show.venue_id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time.strftime('%Y-%m-%d %H:%I')
        }
        past_shows.append(past_show)
    artist.past_shows = past_shows
    artist.past_shows_count = len(past_shows)
    artist.upcoming_shows = upcoming_shows
    artist.upcoming_shows_count = len(upcoming_shows)
    artist.genres = json.loads(artist.genres)
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('pages/show_artist.html', artist=artist)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  error = False
  try:
    artist = Artist.query.filter(Artist.id == artist_id).first()
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    form.image_link.data = artist.image_link
    form.genres.data = json.loads(artist.genres)
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    data = artist
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('forms/edit_artist.html', form=form, artist=data)
  # TODO: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_venue = request.form.get('seeking_venue')
  seeking_description = request.form.get('seeking_description')
  # TODO: modify data to be the data object returned from db insertion
  try:
    Artist.query.filter(Artist.id == artist_id).update({
      'name': name,
      'city': city,
      'state': state,
      'phone': phone,
      'genres': json.dumps(genres),
      'facebook_link': facebook_link,
      'image_link': image_link,
      'website_link': website_link,
      'seeking_venue': seeking_venue,
      'seeking_description': seeking_description
    })
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash("Oops! Something went wrong")
      abort(400)
    else:
     return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  error = False
  form = VenueForm()
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()
    data = venue
    form["name"].data = venue["name"]
    form["genres"].data = venue["genres"]
    form["address"].data = venue["address"]
    form["city"].data = venue["city"]
    form["state"].data = venue["state"]
    form["phone"].data = venue["phone"]
    form["website"].data = venue["website_link"]
    form["facebook_link"].data = venue["facebook_link"]
    form["seeking_talent"].data = venue["seeking_talent"]
    form["seeking_description"].data = venue["seeking_description"]
    form["image_link"].data = venue["image_link"]
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('forms/edit_venue.html', form=form, venue=data.venue)

  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  name = request.form.get("name")
  genres = request.form.get("genres")
  address = request.form.get("address")
  city = request.form.get("city")
  state = request.form.get("state")
  phone = request.form.get("phone")
  website = request.form.get("website")
  facebook_link = request.form.get("facebook_link")
  seeking_talent = request.form.get("seeking_talent")
  seeking_description = request.form.get("seeking_description")
  image_link = request.form.get("image_link")
  try:
    Venue.query.filter(Venue.id == venue_id).update({
      "name" : name,
      "genres" : genres,
      "address" : address,
      "city" : city,
      "state" : state,
      "phone" : phone,
      "website" : website,
      "facebook_link" : facebook_link,
      "seeking_talent" : seeking_talent,
      "seeking_description" : seeking_description,
      "image_link" : image_link,
    })
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('Oops! Somwthing went wrong')
      abort(400)
    else:
      return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
  seeking_description = request.form.get('seeking_description')
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres= json.dumps(genres),
      facebook_link=facebook_link,
      image_link=image_link,
      website_link=website_link,
      seeking_venue=seeking_venue,
      seeking_description=seeking_description
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash("Oops! Something went wrong")
      abort(400)
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  error = False
  try:
    query = db.session.query(Show, Artist, Venue).join(Artist).join(Venue).filter(Show.start_time < datetime.now()).order_by('start_time').all()
    shows = []
    for show in query:
      res = {
        'venue_id': show.Venue.id,
        'venue_name': show.Venue.name,
        'artist_id': show.Artist.id,
        'artist_name': show.Artist.name,
        'artist_image_link': show.Artist.image_link,
        'start_time': show.Show.start_time.strftime('%Y-%m-%d %H:%I')
      }
      shows.append(res)
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  # called to create new shows in the db, upon submitting new show listing form
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  try:
    artist = Artist.query.filter(Artist.id == artist_id).first()
    venue = Venue.query.filter(Venue.id == venue_id).first()
    if not artist.id or not venue.id:
      raise Exception('incorrect id')
    show = Show(artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash("Oops! Something went wrong")
      abort(400)
    else:
      flash('Show was successfully listed!')
      return render_template('pages/home.html')

  # TODO: insert form data as a new Show record in the db, instead
  # try:
  #   show = Show(artist_id=artist_id, venue_id=venue_id,)
  # except:
  # finally:
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
