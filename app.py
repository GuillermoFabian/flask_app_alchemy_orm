#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
from sqlalchemy import func
import babel
from flask import (Flask,
                   render_template,
                   request,
                   Response,
                   flash,
                   redirect,
                   url_for
                   )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from forms import *
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)
#csrf = CSRFProtect(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


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
    locals = []
    venues = Venue.query.all()
    places = Venue.query.distinct(Venue.city, Venue.state).all()

    for place in places:
        for venue in venues:
            if venue.city == place.city and venue.state == place.state:
                locals.append({
                    'city': place.city,
                    'state': place.state,
                    'venues': [{
                        'id': venue.id,
                        'name': venue.name,
                        'num_upcoming_shows': len(
                            [show for show in venue.shows if show.start_date > datetime.now()])
                    }]
                })

    return render_template('pages/venues.html', areas=locals, venues=venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  term = request.form.get('search_term', '').lower()
  search = "%{}%".format(term)
  venues = Venue.query.filter(Venue.name.ilike(search)).all()

  def upcoming_shows(id):
      shows = db.session.query(Show).join(Venue).filter(Venue.id == id).all()
      upcoming_shows = []
      if shows is not None:
          for show in shows:
              if show.start_date > datetime.now():
                  upcoming_shows.append({
                      "show_id": show.id
                  })
      return upcoming_shows
  data=[]
  for venue in venues:
      info = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows(venue.id))
      }
      data.append(info)
  response1 = {
      "count": Venue.query.filter(Venue.name.ilike(search)).count(),
      "data": data
  }


  return render_template('pages/search_venues.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue= Venue.query.first_or_404(venue_id)
  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
      temp_show = {
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_date.strftime("%m/%d/%Y, %H:%M")
      }
      if show.start_date <= datetime.now():
          past_shows.append(temp_show)
      else:
          upcoming_shows.append(temp_show)

  data = vars(venue)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data )

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form,
                   meta={'csrf': False}
                   )
  if form.validate():
      try:
          venue = Venue()
          form.populate_obj(venue)
          db.session.add(venue)
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
      except:
          flash('An error occurred. Artist ' + form.name.data + 'could not be added')
      finally:
          db.session.close()
  else:
      message = []
      for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
      flash('Errors ' + str(message))

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      flash('Venue id ' + venue_id + ' was successfully deleted!')
  except:
      flash('An error occurred. Venue id' + venue_id + 'could not be deleted!')
      db.session.rollback()
  finally:
      db.session.close()
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data1 = []
  for artist in artists:
      data = {
          "id": artist.id,
          "name": artist.name,
      }
      data1.append(data)
  return render_template('pages/artists.html', artists=data1)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  term = request.form.get('search_term', '').lower()
  search = "%{}%".format(term)
  artists = Artist.query.filter(Artist.name.ilike(search)).all()

  def upcoming_shows(id):
      shows = db.session.query(Show).join(Artist).filter(Artist.id == id).all()
      upcoming_shows = []
      if shows is not None:
          for show in shows:
              if show.start_date > datetime.now():
                  upcoming_shows.append({
                      "show_id": show.id
                  })
      return upcoming_shows

  data = []
  for artist in artists:
      info = {
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(upcoming_shows(Artist.id))
      }
      data.append(info)
  response1 = {
      "count": Artist.query.filter(Artist.name.ilike(search)).count(),
      "data": data
  }

  return render_template('pages/search_artists.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.first_or_404(artist_id)

    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        temp_show = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_date.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_date <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    data = vars(artist)
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_data = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(obj=artist_data)

  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(request.form)

  if artist:
      try:
        artist.name=form.name.data
        artist.genres=form.genres.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.website=form.website_link.data
        artist.facebook_link=form.facebook_link.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
        artist.image_link=form.image_link.data
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully updated!')
      except:
        flash('An error occurred. Artist ' + form.name.data + 'could not be updated')
      finally:
        db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
      Artist.query.filter_by(id=artist_id).delete()
      db.session.commit()
      flash('Artist id' + artist_id + 'was successfully deleted!')
  except ValueError as e:
      flash('An error occurred. Artist id' + artist_id + 'could not be deleted!')
      db.session.rollback()
  finally:
      db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_data = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(obj=venue_data)

  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(request.form)

  if venue:
      try:
          venue.name = form.name.data
          venue.genres = form.genres.data
          venue.city = form.city.data
          venue.state = form.state.data
          venue.phone = form.phone.data
          venue.website = form.website_link.data
          venue.facebook_link = form.facebook_link.data
          venue.seeking_talent = form.seeking_talent.data
          venue.seeking_description = form.seeking_description.data
          venue.image_link = form.image_link.data
          db.session.commit()
          flash('Venue ' + form.name.data + ' was successfully updated!')
      except:
          flash('An error occurred. Venue ' + form.name.data + 'could not be updated')
      finally:
          db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    artist = Artist(
        name=form.name.data,
        genres=form.genres.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        website=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
        image_link=form.image_link.data,
    )
    try:
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + form.name.data + 'could not be added')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data1 = []
  for show in shows:
      data = {

          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_date))
      }
      data1.append(data)


  return render_template('pages/shows.html', shows=data1)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  show = Show(
      start_date=form.start_time.data,
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
  )
  try:
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
  except:
      flash('An error occurred. Show could not be listed')
  finally:
      db.session.close()

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
