#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
from tkinter import N
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import null
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# app = Flask(__name__)
# moment = Moment(app)
# app.config.from_object('config')
# db = SQLAlchemy(app)

# migrate = Migrate(app, db)

app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)

# TODO: connect to a local postgresql database
#DONE: Connection to the local postgresql database has been made in the config.py file
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# DONE: All models implemented
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------

@app.route('/')
def index():
    recent_artists = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
    recent_venues = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
    return render_template('pages/home.html', artists=recent_artists, venues=recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    fetch_results = Venue.query.order_by(Venue.city, Venue.state).all()

    for result in fetch_results:
        venues = Venue.query.filter_by(
            city=result.city, state=result.state).all()
        datum = {
            "city": result.city,
            "state": result.state,
            "venues": []
        }

        data.append(datum)

        for venue in venues:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
            data[-1]["venues"].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > current_time).all()),
            })

    return render_template('pages/venues.html', areas=data)


# The search venues module
# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
# seach for Hop should return "The Musical Hop".
# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

@app.route('/venues/search', methods=['GET', 'POST'])
def search_venues():

    # Defining the term searched for
    s_term = request.form.get("search_term", "")

    # Defining the server response
    response = {}

    # Performing the search for the table columns, name, city and state
    s_results = list(Venue.query.filter(
        Venue.name.ilike(f"%{s_term}%") |

        Venue.city.ilike(f"%{s_term}%") |

        Venue.state.ilike(f"%{s_term}%")).all())

    response["count"] = len(s_results)
    response["data"] = []

    # Looping through the results to display
    for s_result in s_results:
        venue = {
            "id": s_result.id,
            "name": s_result.name,
            "num_upcoming_shows": len(Show.query.filter(Show.venue_id == s_result.id).filter(Show.start_time > datetime.now()).all())
        }
        response["data"].append(venue)

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


# The single venue module
# shows the venue page with the given venue_id
# TODO: replace with real venue data from the venues table, using venue_id

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    
    venue = Venue.query.get(venue_id)

    # Upcoming shows
    upcoming_shows_fetch = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
    upcoming_shows = []

    for upcoming_show in upcoming_shows_fetch:
        upcoming_shows.append({
        "artist_id": upcoming_show.artist_id,
        "artist_name": upcoming_show.artist.name,
        "artist_image_link": upcoming_show.artist.image_link,
        "start_time": upcoming_show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })


    # Past shows
    past_shows_fetch = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
    past_shows = []

    for past_show in past_shows_fetch:
        past_shows.append({
        "artist_id": past_show.artist_id,
        "artist_name": past_show.artist.name,
        "artist_image_link": past_show.artist.image_link,
        "start_time": past_show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
        }

    return render_template('pages/show_venue.html', venue=data)
    

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


# The create venues module
# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
       
    try:
        recent_venue = Venue()

        recent_venue.name = form.name.data
        recent_venue.city = form.city.data
        recent_venue.state = form.state.data
        recent_venue.address = form.address.data
        recent_venue.phone = form.phone.data
        recent_venue.image_link = form.image_link.data
        recent_venue.facebook_link = form.facebook_link.data
        recent_venue.genres = form.genres.data
        recent_venue.website = form.website_link.data
        recent_venue.seeking_description = form.seeking_description.data

        db.session.add(recent_venue)
        db.session.commit()

        # on successful db insert, flash success
        # flash('Venue ' + request.form['name'] + ' was successfully listed!')
        flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

        db.session.rollback()
        flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')

    finally:
        db.session.close()

    return redirect(url_for("index"))


# EDIT Venue module ---------------------------------------------------------
# TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)

  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)


# TODO: take values from the form submitted, and update existing
# venue record with ID <venue_id> using the new attributes
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    
    try:
        venue = Venue.query.get(venue_id)

        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.genres = form.genres.data
        venue.image_link = form.image_link.data
        venue.website = form.website_link.data
        venue.seeking_description = form.seeking_description.data

        db.session.add(venue)
        db.session.commit()

        flash("Venue " + form.name.data + " was successfully edited")
    except:
        db.session.rollback()
        flash("Venue was not successfully edited.")
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


# DELETE Venue module ---------------------------------------------------------------

# TODO: Complete this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
# clicking that button delete it from the db then redirect the user to the homepage

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    
    try:
        venue_to_delete = Venue.query.get(venue_id)
        db.session.delete(venue_to_delete)
        db.session.commit()
        flash('Venue ' + venue_to_delete.name + ' was successfully deleted!')

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Venue ' + venue_to_delete.name + ' could not be deleted, please try again.')

    finally:
        db.session.close()

    return redirect(url_for('index'))


#  Artists module-----------------------------------------------------------
# TODO: replace with real data returned from querying the database

@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


# The artist search module ..................................................................
# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
# search for "band" should return "The Wild Sax Band".
@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form.get('search_term', '')
    marching_results = Artist.query.filter(
        Artist.name.ilike(f"%{search_term}%") |
        Artist.city.ilike(f"%{search_term}%") |
        Artist.state.ilike(f"%{search_term}%")
    ).all()
    data = []

    for artist in marching_results:
        datum = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(Show.query.filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()),
    }

    data.append(datum)
  
    response={
        "count": len(marching_results),
        "data": data
    }
    
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


# shows the artist page with the given artist_id
# TODO: replace with real artist data from the artist table, using artist_id
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    
    artist = Artist.query.get(artist_id)

    # Past shows
    past_shows_fetch = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
    past_shows = []

    for past_show in past_shows_fetch:
        past_shows.append({
        "venue_id": past_show.venue_id,
        "venue_name": past_show.venue.name,
        "artist_image_link": past_show.venue.image_link,
        "start_time": past_show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

    # Upcoming shows
    upcoming_shows_fetch = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
    upcoming_shows = []

    for upcoming_show in upcoming_shows_fetch:
        upcoming_shows.append({
        "venue_id": upcoming_show.venue_id,
        "venue_name": upcoming_show.venue.name,
        "artist_image_link": upcoming_show.venue.image_link,
        "start_time": upcoming_show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

    data={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
        }

    return render_template('pages/show_artist.html', artist=data)
    

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist: 
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.website_link.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


# TODO: take values from the form submitted, and update existing
# artist record with ID <artist_id> using the new attributes
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)

    try:
        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.website = form.website_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data
        

        db.session.add(artist)
        db.session.commit()
        flash("Artist " + form.name.data + " edited successfully")
    except:
        db.session.rollback()
        flash("Artist " + form.name.data + "'s information was not successfully edited.")
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))



#  Create Artist ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


# called upon submitting the new artist listing form
# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion 
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form) 

    try:
        recent_artist = Artist()

        recent_artist.name = form.name.data
        recent_artist.city = form.city.data
        recent_artist.state = form.state.data
        recent_artist.phone = form.phone.data
        recent_artist.image_link = form.image_link.data
        recent_artist.facebook_link = form.facebook_link.data
        recent_artist.genres = form.genres.data
        recent_artist.website = form.website_link.data
        recent_artist.seeking_description = form.seeking_description.data

        db.session.add(recent_artist)
        db.session.commit()

        # on successful db insert, flash success
        # flash('Artist ' + request.form['name'] + ' was successfully listed!')
        flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for("index"))


#  Shows ----------------------------------------------------------------
# displays list of shows at /shows
# TODO: replace with real venues data.
@app.route('/shows')
def shows():
    
    all_shows = Show.query.all()
    data = []

    for show in all_shows:
        datum = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
         }

        data.append(datum)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


# called to create new shows in the db, upon submitting new show listing form
# TODO: insert form data as a new Show record in the db, instead
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    try:
        recent_show = Show()

        recent_show.artist_id = form.artist_id.data
        recent_show.venue_id = form.venue_id.data
        recent_show.start_time = form.start_time.data

        db.session.add(recent_show)
        db.session.commit()
        
      # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
