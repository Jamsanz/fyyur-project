import imp
import sys
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from models.venue import Venue
from forms import *
from models.artist import Artist
from models.db import db
from models.show import Show


def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  error = False
  try:
    query = db.session.query(Show, Artist, Venue).join(Artist).join(
        Venue).filter(Show.start_time < datetime.now()).order_by('start_time').all()
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


def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

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
