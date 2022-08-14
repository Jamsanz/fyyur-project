import sys
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from models.venue import Venue
from forms import *
from models.artist import Artist
from models.db import db
import json


def artists():
  return render_template('pages/artists.html', artists=Artist.getAllArtists(Artist))


def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  error = False
  search_term = request.form.get('search_term')
  try:
    results = Artist.searchArtist(Artist, search_term)
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
    artist = Artist.getArtistById(Artist, artist_id)
    for show in artist.shows:
      if datetime.now() < show.start_time:
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
  form = ArtistForm(request.form)
  artist = Artist(
    name=form.name.data,
    city=form.city.data,
    state=form.state.data,
    phone=form.phone.data,
    genres=json.dumps(form.genres.data),
    facebook_link=form.facebook_link.data,
    image_link=form.image_link.data,
    website_link=form.website_link.data,
    seeking_venue=form.seeking_venue.data,
    seeking_description=form.seeking_description.data
  )
  if form.validate():
    Artist.create(artist)
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('Incorrect phone number')
    return redirect(url_for('artist_bp.create_artist_form'))

  return render_template('pages/home.html')

def edit_artist(artist_id):
  form = ArtistForm()
  error = False
  try:
    artist = Artist.getArtistById(Artist, artist_id)
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


def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm(request.form)
  try:
    update_artist = Artist.getArtistById(Artist, artist_id)
    update_artist.name = form.name.data
    update_artist.genres = json.dumps(form.genres.data)
    update_artist.city = form.city.data
    update_artist.state = form.state.data
    update_artist.phone = form.phone.data
    update_artist.website_link = form.website_link.data
    update_artist.facebook_link = form.facebook_link.data
    update_artist.seeking_talent = form.seeking_talent.data
    update_artist.seeking_description = form.seeking_description.data
    update_artist.image_link = form.image_link.data

    if form.validate():
      Venue.update(update_artist)
    else:
      flash('Please check all fields')
  except:
    error = True
  finally:
    if error:
      flash('Oops! Somwthing went wrong')
      abort(400)
    else:
      return redirect(url_for('artist_bp.show_artist', venue_id=artist_id))


def delete_artist(artist_id):
  error = False
  try:
    Artist.query.filter(Artist.id == artist_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash("Oops! cannot delete this artist because he/she is linked to a show")
      abort(400)
    else:
      flash('Successfully deleted')
      return redirect(url_for('home_bp.index'))
      

  # TODO: populate form with fields from artist with ID <artist_id>
