from models.db import db
import sys

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
  website_link = db.Column(db.String(120), nullable=True)
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True)
  shows = db.relationship('Show', backref='artist', lazy=True)

  def create(self):
    try:
      db.session.add(self)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

  def getAllArtists(self):
   return self.query.with_entities(self.id, self.name).all()

  def searchArtist(self, search_term):
    return self.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

  def getArtistById(self, artist_id):
    return self.query.filter(Artist.id==artist_id).first()

  def update(self):
    try:
      db.session.add(self)
      db.session.commit()
    except:
      db.session.rollbac()
      print(sys.exc_info())
    finally:
      db.session.close()

  def delete(self):
    try:
      db.session.delete(self)
      db.session.commit()
    except:
      db.session.rollbac()
      print(sys.exc_info())
    finally:
      db.session.close()
