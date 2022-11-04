from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    Migrate(app, db)
    return db

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True, unique=True)
    image_link = db.Column(db.String(500), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120), nullable=True, unique=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean(), nullable=True)
    seeking_description = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return str(self.__dict__)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True, unique=True)
    image_link = db.Column(db.String(500), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120), nullable=True, unique=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean(), nullable=True)
    seeking_description = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return str(self.__dict__)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.TIMESTAMP(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)

    venue = db.relationship(
        "Venue", backref=db.backref("shows", cascade="all,delete"), lazy=True
    )

    artist = db.relationship(
        "Artist", backref=db.backref("shows", cascade="all,delete"), lazy=True
    )
    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

