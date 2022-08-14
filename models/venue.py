from models.db import db
import sys
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
  seeking_description = db.Column(db.String(500), nullable=True)
  shows = db.relationship('Show', backref='venue', lazy=True)

  def serialize(self):
      return {
          'name': self.name,
          'city': self.city,
          'state': self.state,
          'genres': self.genres,
          'seeking_talent': self.seeking_talent
      }
  
  def create(self):
    try:
      db.session.add(self)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

  def getAllVenues(self):
    return self.query.all()
  
  def getVenueById(self, venue_id):
    return self.query.filter(Venue.id == venue_id).first()
  
  def searchVenue(self, search_term):
    return self.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
  
  

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
