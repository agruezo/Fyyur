#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from model import Venue, Artist, Show, init_db
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = init_db(app)

# TODO: connect to a local postgresql database

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
  data = []
  current_time = datetime.now()
  venues = Venue.query.order_by(Venue.city).all()
  dict = {}
  cities = []

  venues_list = []

  for venue in venues:
    num_shows = 0

    for show in venue.shows:
      if (show.start_time > current_time):
        num_shows += 1

    if venue.city not in cities:
      venues_list = [
        {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_shows,
        }
      ]
      dict = {
        "city": venue.city,
        "state": venue.state,
        "venues": venues_list
      }
      cities.append(venue.city)
      data.append(dict)
    else:
      new_venue = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_shows,
      }
      venues_list.append(new_venue)
      data[-1]['venues'] = venues_list

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  form = "%{}%".format(search_term)
  result = Venue.query.filter(Venue.name.ilike(form)).all()
  response = {
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  shows = venue.shows
  past_shows = []
  upcoming_shows = []

  for show in shows:
    if show.start_time <= datetime.now():
      past_shows.append({
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          "artist_image_link": show.artist.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
    else:
      upcoming_shows.append({
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        "artist_image_link": show.artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False

  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    genres = request.form.get('genres')
    phone = request.form.get('phone')
    address = request.form.get('address')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')

    venue = Venue(
      name=name, 
      city=city, 
      state=state, 
      genres=genres, 
      phone=phone, 
      address=address,
      seeking_talent=True if seeking_talent == "y" else False, 
      seeking_description=seeking_description, website_link=website_link, 
      facebook_link=facebook_link, 
      image_link=image_link
      )
    db.session.add(venue)
    db.session.commit()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    error = True
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be deleted.')
    db.session.rollback()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
    dict = {
      "id": artist.id,
      "name": artist.name,
    }
    data.append(dict)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  form = "%{}%".format(search_term)
  result = Artist.query.filter(Artist.name.ilike(form)).all()
  response = {
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist = Artist.query.get(artist_id)
  shows = artist.shows
  past_shows = []
  upcoming_shows = []
    
  for show in shows:
    if show.start_time > datetime.now():
      upcoming_shows.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          "venue_image_link": show.venue.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        })
    else:
      past_shows.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          "venue_image_link": show.venue.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).one()
  form = ArtistForm(
    name=artist.name,
    city=artist.city,
    state=artist.state,
    genres=artist.genres,
    phone=artist.phone,
    seeking_venue=artist.seeking_venue,
    seeking_description=artist.seeking_description,
    website_link=artist.website_link,
    facebook_link=artist.facebook_link,
    image_link=artist.image_link
    )

  # TODO: populate form with fields from artist with ID <artist_id>

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False

  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    genres = request.form.get('genres')
    phone = request.form.get('phone')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')

    artist = {
      "name": name, 
      "city": city, 
      "state": state, 
      "genres": genres, 
      "phone": phone, 
      "seeking_venue": True if seeking_venue == "y" else False,
      "seeking_description": seeking_description,
      "website_link": website_link, 
      "facebook_link": facebook_link, 
      "image_link": image_link}

    Artist.query.filter(Artist.id == artist_id).update(artist)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be updated.')
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + request.form.get('name') + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id).one()
  form = VenueForm(
    name=venue.name,
    city=venue.city,
    state=venue.state,
    genres=venue.genres,
    phone=venue.phone,
    address=venue.address,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description,
    website_link=venue.website_link,
    facebook_link=venue.facebook_link,
    image_link=venue.image_link
    )
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False

  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    genres = request.form.get('genres')
    phone = request.form.get('phone')
    address = request.form.get('address')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')

    venue = {
      "name": name, 
      "city": city, 
      "state": state, 
      "genres": genres, 
      "phone": phone, 
      "address": address, 
      "seeking_talent": True if seeking_talent == "y" else False,
      "seeking_description": seeking_description,
      "website_link": website_link, 
      "facebook_link": facebook_link, 
      "image_link": image_link
      }

    Venue.query.filter(Venue.id == venue_id).update(venue)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form.get('name') + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False

  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    genres = request.form.get('genres')
    phone = request.form.get('phone')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')

    artist = Artist(
      name=name, 
      city=city, 
      state=state, 
      genres=genres, 
      phone=phone,
      seeking_venue=True if seeking_venue == "y" else False, 
      seeking_description=seeking_description, website_link=website_link, facebook_link=facebook_link, 
      image_link=image_link
      )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  dict = {}
  shows = Show.query.all()
  for show in shows:
    dict = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      }
    data.append(dict)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm()

  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Show was successfully listed!')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
