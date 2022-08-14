import sys
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from models.venue import Venue
from forms import *
from models.artist import Artist
from models.db import db
import json


def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  error = False
  response = []
  try:
    venues = Venue.getAllVenues(Venue)
    for venue in venues:
      res = {
          'city': venue.city,
          'state': venue.state,
          'venues': []
      }
      shows_count = 0
      for show in venue.shows:
        if show.start_time > datetime.now():
          shows_count = shows_count + 1
      res['venues'].append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': shows_count
      })
      response.append(res)
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('pages/venues.html', areas=response)


def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  error = False
  search_term = request.form.get('search_term')
  try:
    results = Venue.searchVenue(Venue, search_term)
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


def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error = False
  past_shows = []
  upcoming_shows = []
  try:
    venue = Venue.getVenueById(Venue, venue_id)
    for show in venue.shows:
      if datetime.now() > show.start_time:
        artist = Artist.query.filter(Artist.id == show.artist_id).first()
        past_show = {
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%I')
        }
        past_shows.append(past_show)
      else:
        artist = Artist.query.filter(Artist.id == show.artist_id).first()
        upcoming_show = {
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%I')
        }
        upcoming_shows.append(upcoming_show)
    venue.upcoming_shows = upcoming_shows
    venue.upcoming_shows_count = len(upcoming_shows)
    venue.past_shows = past_shows
    venue.past_shows_count = len(past_shows)
    venue.genres = json.loads(venue.genres)
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


def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


def create_venue_submission():
  error = False
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=json.dumps(form.genres.data),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
  )
  if form.validate():
    Venue.create(venue)
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('Incorrect phone number')
  return redirect(url_for('venue_bp.create_venue_form'))

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


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
      flash("Oops! cannot delete this venue because it's attached to a show")
      abort(400)
    else:
      flash('Successfully deleted')
      return redirect(url_for('home_bp.index'))
 # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


def edit_venue(venue_id):
  error = False
  form = VenueForm()
  try:
    venue = Venue.getVenueById(Venue, venue_id)
    data = venue
    form["name"].data = venue.name
    form["genres"].data = venue.genres
    form["address"].data = venue.address
    form["city"].data = venue.city
    form["state"].data = venue.state
    form["phone"].data = venue.phone
    form["website_link"].data = venue.website_link
    form["facebook_link"].data = venue.facebook_link
    form["seeking_talent"].data = venue.seeking_talent
    form["seeking_description"].data = venue.seeking_description
    form["image_link"].data = venue.image_link
  except:
    error = True
    print(sys.exc_info())
  finally:
    if error:
      flash("Oops! Something went wrong")
      abort(500)
    else:
      return render_template('forms/edit_venue.html', form=form, venue=data)


def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm(request.form)
  try:
    update_venue = Venue.getVenueById(Venue, venue_id)
    update_venue.name = form.name.data
    update_venue.genres = json.dumps(form.genres.data)
    update_venue.address = form.address.data
    update_venue.city = form.city.data
    update_venue.state = form.state.data
    update_venue.phone = form.phone.data
    update_venue.website_link = form.website_link.data
    update_venue.facebook_link = form.facebook_link.data
    update_venue.seeking_talent = form.seeking_talent.data
    update_venue.seeking_description = form.seeking_description.data
    update_venue.image_link = form.image_link.data

    if form.validate():
      Venue.update(update_venue)
    else:
      flash('Please check all fields')
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('Oops! Somwthing went wrong')
      abort(400)
    else:
      return redirect(url_for('venue_bp.show_venue', venue_id=venue_id))
