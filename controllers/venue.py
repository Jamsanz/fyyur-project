import sys
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from models.venue import Venue
from forms import *
from models.artist import Artist
from models.db import db

def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = [{
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
  return render_template('pages/venues.html', areas=data)



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


def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)



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
        "name": name,
        "genres": genres,
        "address": address,
        "city": city,
        "state": state,
        "phone": phone,
        "website": website,
        "facebook_link": facebook_link,
        "seeking_talent": seeking_talent,
        "seeking_description": seeking_description,
        "image_link": image_link,
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
