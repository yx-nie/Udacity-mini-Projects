#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate=Migrate(app, db)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link=db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(500))
    genres=db.Column(db.String(120))  
    shows=db.relationship('Show', backref=db.backref('venue', lazy=True), lazy=True)
    


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
    website_link=db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(500))
    shows=db.relationship('Show', backref=db.backref('artist', lazy=True), lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
    __tablename__='Show'

    id= db.Column(db.Integer, primary_key=True)
    venue_id=db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id=db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    datetime=db.Column(db.DateTime, nullable=False)
    
    
    





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

  data=[]
  venues=Venue.query.all()
  count=db.func.count(Venue.city)
  city_state=db.session.query(Venue.city, Venue.state, count).group_by(Venue.city, Venue.state).all()
  
  for item in city_state:
    data.append({
      "city": item.city,
      "state": item.state,
      "venues": Venue.query.filter(Venue.city==item.city, Venue.state==item.state).all()
    })
    
 
  return render_template('pages/search_venues.html', results=response)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue_info=Venue.query.get(venue_id)

  shows=Show.query.filter(Show.venue_id==venue_id).all()
  upcoming_shows=[]
  upcoming_shows_count=0
  past_shows=[]
  past_shows_count=0
  for show in shows:
    if show.datetime>datetime.now():
      upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "datetime": format_datetime(str(show.datetime))
      })
      upcoming_shows_count =+1
    if show.datetime<datetime.now():
      past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "datetime": format_datetime(str(show.datetime))
      })
      past_shows_count =+1
  
  venue_info.upcoming_shows=upcoming_shows
  venue_info.upcoming_shows_count=upcoming_shows_count
  venue_info.past_shows=past_shows
  venue_info.past_shows_count=past_shows_count

  return render_template('pages/show_venue.html', venue=venue_info)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  data_form=request.form
  venue_form=VenueForm(meta={'csrf':False})
  # set the venue_form is not a cross site request forgery(csrf)

  if not venue_form.validate_on_submit():
     for error in venue_form.errors.keys():
       flash('validataion error at'+ error)
     return render_template('forms/new_venue.html', form=venue_form)
  # validata the form fistly
   
  try:
    new_venue=Venue(**venue_form.data)
    db.session.add(new_venue)
    db.session.commit()
    flash('new venue '+new_venue.name+' is listed successfully','alert-success')

  except Exception as e:
    print(e)
    db.session.rollback()
    flash('Error in creating venue  ' + data_form['name'],'alert-danger')
  finally:
    db.session.close()
    
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue_dele=db.session.query.filter(Venue.id==venue_id).all()
    db.session.delete(Venue.id==venue_id)
    db.commit()
    flash('the action to delete the venue '+ venue_dele.name + ' successed')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('the action to delete the venue '+ venue_dele.name + ' failed')
  finally:
    db.session.close()


  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  
  data=Artist.query.all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_name=Artist.name.ilike('%{}%'.format(request.form.get('search_term', '')))
  search_result=Artist.query.filter(search_name).all()
 
  
  response={
    "count": len(search_result),
    "data": []
    }
  for item in search_result:
    dataset={
      "id": item.id,
      "name": item.name,
      "num_upcoming_shows": len(Artist.query.filter(Show.artitst_id==item.id, Show.datetime>datetime.now()).all())
    }
  response['data'].append(dataset)
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  data=Artist.query.get(artist_id)

  shows=Show.query.filter(Show.artist_id==artist_id).all()
  upcoming_shows=[]
  upcoming_shows_count=0
  past_shows=[]
  past_shows_count=0
  
  for show in shows:
    if show.datetime>datetime.now():
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "datetime": format_datetime(str(show.datetime))
        })
      upcoming_shows_count =+1

    if show.datetime<datetime.now():
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "datetime": format_datetime(str(show.datetime))
        })
      past_shows_count =+1
  
  data.upcoming_shows=upcoming_shows
  data.upcoming_shows_count=upcoming_shows_count
  data.past_shows=past_shows
  data.past_shows_count=past_shows_count


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist_edit=Artist.query.get(artist_id)
  artist={
    "id": artist_edit.id,
    "name": artist_edit.name,
    "genres": artist_edit.genres,
    "city": artist_edit.city,
    "state": artist_edit.state,
    "phone": artist_edit.phone,
    "website": artist_edit.website_link,
    "facebook_link": artist_edit.facebook_link,
    "seeking_venue": artist_edit.seeking_venue,
    "seeking_description": artist_edit.seeking_description,
    "image_link": artist_edit.image_link
  }
  form = ArtistForm(**artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist=Artist.query.get(artist_id)

  edit_artist_submit=ArtistForm(meta={'csrf': False})
  if not edit_artist_submit.validate_on_submit():
    for error in edit_artist_submit.errors.keys():
       flash('validataion error at '+ error,'alert-warning')
    return redirect(url_for('edit_artist', artist_id=artist_id))

  try:
    to_submit_artist=Artist(**edit_artist_submit.data)
    artist.name=to_submit_artist.name
    artist.genres=to_submit_artist.genres
    artist.city=to_submit_artist.city
    artist.state=to_submit_artist.state
    artist.phone=to_submit_artist.phone
    artist.website_link=to_submit_artist.website_link
    artist.facebook_link=to_submit_artist.facebook_link
    artist.seeking_venue=to_submit_artist.seeking_venue
    artist.seeking_description=to_submit_artist.seeking_description
    artist.image_link=to_submit_artist.image_link
    db.session.commit()
    flash('the artist '+ to_submit_artist.name+' has been successfully edited!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('the artist '+artist.name+' failed in edition')
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  

  venue=Venue.query.get(venue_id)
  venues={
     "name":venue.name,
     "genres":venue.genres,
     "address":venue.address,
     "city":venue.city,
     "state":venue.state,
     "phone":venue.phone,
     "website":venue.website_link,
     "facebook_link":venue.facebook_link,
     "seeking_talent":venue.seeking_talent,
     "seeking_description":venue.seeking_description,
     "image_link":venue.image_link
  }
  form = VenueForm(**venues)


  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(meta={'csrf': False})
  if not form.validate_on_submit():
    for error in form.errors.keys():
      flash('validation errors '+ error,' alert-warning')
      return render_template('forms/edit_venue.html', form=form, venue=venue)
  try:
    newform=Venue(**form.data)
    venue.name=newform.name
    venue.genres=newform.genres
    venue.address=newform.address
    venue.city=newform.city
    venue.state=newform.state
    venue.phone=newform.phone
    venue.website_link=newform.website_link
    venue.facebook_link=newform.facebook_link
    venue.seeking_talent=newform.seeking_talent
    venue.seeking_description=newform.seeking_description
    venue.image_link=newform.image_link
    db.session.commit()
    flash(newform.name+' has been successfully edited','alert-success')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash(venue.name+' failed in edition', 'alert-warning')
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
  artist_exist=request.form
  artist_sub=ArtistForm(meta={'csrf':False})

  if not artist_sub.validate_on_submit():
    for error in artist_sub.errors.keys():
      flash('validata errors '+error, 'alert-warning')
      return render_template('forms/new_artist.html', form=artist_sub)
  
  try:
    to_sub_artist=Artist(**artist_sub.data)
    db.session.add(to_sub_artist)
    db.session.commit()
    flash('Aritst '+ to_sub_artist.name+' has been inserted into db', 'alert-success')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('Artist '+ artist_exist['name']+' failed in insertion', 'alert-warning')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[]
  shows=Show.query.all()
  for show in shows:
    data.append({
      "venue_id":show.venue_id,
      "venue_name": show.venue.name,
      "artist_id":show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "datetime":format_datetime(str(show.datetime))
    })


  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form=request.form
  new_show=ShowForm(meta={'csrf':False})

  if not new_show.validate_on_submit():
    for error in new_show.errors.keys():
      flash('validate errors '+ error, 'alert-warning')
      return render_template('forms/new_show.html', form=form)

  try:
    insertion=Show(**new_show.data)
    db.session.add(insertion)
    db.session.commit()
    flash('Show was successfully listed!')

  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred'+form['artist_id']+' could not be listed.')

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
