from models.db import db

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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
