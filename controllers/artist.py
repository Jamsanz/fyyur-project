import sys
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from models.venue import Venue
from forms import *
from models.artist import Artist
from models.db import db
import json

def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)


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


def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  error = False
  upcoming_shows = []
  past_shows = []
  try:
    artist = Artist.query.filter(Artist.id == artist_id).first()
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


def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


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
        genres=json.dumps(genres),
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
