#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#import the variable SQLALCHEMY_DATABASE_URI from config.py
from config import SQLALCHEMY_DATABASE_URI
#import Migrate
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# The Show table should presented here to avoid errors of show is not defined
Show = db.Table('shows',
  db.Column('id' , db.Integer , primary_key = True),
  db.Column('venue_id' , db.Integer , db.ForeignKey('venue.id') ),
  db.Column('artist_id' , db.Integer , db.ForeignKey('artist.id') ),
  db.Column('start_time' , db.DateTime)
)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean , default=False)
    seeking_description = db.Column(db.String(500))

    #make the many to many relationship between Venue and Artist
    artists = db.relationship('Artist' , secondary = Show , backref=db.backref('venue',lazy=True))#,cascade="all, delete"

    def __repr__(self):
        return f'<Venue : {self.name} - city : {self.city} - state : {self.state}>' 



class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_talent = db.Column(db.Boolean , default=False)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(500))
    
    #make the many to many relationship between Venue and Artist
    venues = db.relationship('Venue' , secondary = Show , backref=db.backref('artist',lazy=True))
    
    def __repr__(self):
      return f'Artist : {self.name}'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  #there is an error , I am already make the start time a datetime in my model
  # so I added this condtion
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  print(date)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en')
  #locale='en' added to stop attribute error

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
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    #get all data from venues table sorted to categorize the venues based on the city and states
    data=[]
    sorted_venues = Venue.query.order_by(Venue.state,Venue.city).distinct(Venue.city, Venue.state).all()
    
    for venue in sorted_venues:     
        data.append({
          "city": venue.city,
          "state": venue.state,
          "venues": [{
              "id": another_venue.id,
              "name": another_venue.name,
                            
            }for another_venue in Venue.query.filter_by(city=venue.city, state=venue.state).all()]
        })

    
 
 #  data=[{
 #   "city": "San Francisco",
 #   "state": "CA",
 #   "venues": [{
 #     "id": 1,
 #     "name": "The Musical Hop",
 #     "num_upcoming_shows": 0,
 #   }, {
 #     "id": 3,
 #     "name": "Park Square Live Music & Coffee",
 #     "num_upcoming_shows": 1,
 #   }]
 # }, {
 #   "city": "New York",
 #   "state": "NY",
 #   "venues": [{
 #     "id": 2,
 #     "name": "The Dueling Pianos Bar",
 #     "num_upcoming_shows": 0,
 #   }]
 # }] 
    #data.append(dictionary_data)
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searched_string = request.form.get('search_term')
  result = Venue.query.filter(Venue.name.ilike('%'+ searched_string+'%')).all()
  count = len(result)
  # get all upcoming shows
  #Venue.query.join(shows).filter()
  data=[]
  for venue in result:
    data.append({
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows" : Show.c.venue_id,
    })
  response = {
    "count" : count,
    "data" : data
  }
  '''response={
    "count": count,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  '''
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #get the desired venue
  current_venue = Venue.query.filter_by(id=venue_id).first()
  past_shows = []
  upcoming_shows = []
  current_date = datetime.utcnow()
  #get all shows related to the current venue
  all_shows = db.session.query(Show).filter(Show.c.venue_id == Venue.id).all()
  for show in all_shows:
    #get the artist
    artist = Artist.query.filter_by(id=show.artist_id).first()
    if show.start_time >= current_date:
      upcoming_shows.append({
        "artist_id" : artist.id,
        "artist_name" :artist.name,
        "artist_image_link" : artist.image_link,
        "start_time": show.start_time
      })
    else:
      past_shows.append({
        "artist_id" : artist.id,
        "artist_name" :artist.name,
        "artist_image_link" : artist.image_link,
        "start_time": show.start_time
      })
  no_of_past_shows = len(past_shows)
  no_of_upcoming_shows = len(upcoming_shows)
  data = {
    "id": current_venue.id,
    "name": current_venue.name,
    "genres": current_venue.genres.split(','),
    "address": current_venue.address,
    "city": current_venue.city,
    "state": current_venue.state,
    "phone": current_venue.phone,
    "website": current_venue.website,
    "facebook_link": current_venue.facebook_link,
    "seeking_talent": current_venue.seeking_talent,
    "seeking_description":current_venue.seeking_description,
    "image_link": current_venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": no_of_past_shows,
    "upcoming_shows_count": no_of_upcoming_shows,
  }
  '''data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  ''' 
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
  # get the data from the form
  
  try:
      #venue name 
      venue_name = request.form.get('name')

      #venue city and state
      venue_city = request.form.get('city')
      venue_state = request.form.get('state')

      #venue address
      venue_address = request.form.get('address')

      #venue phone
      venue_phone = request.form.get('phone')

      #venue geners 
      venue_genres = request.form.getlist('genres')
      #construct your list [,,,]
      venue_genres = ','.join(venue_genres)

      #venue facebook
      venue_facebook_link = request.form.get('facebook_link')

      #venue website
      venue_website_link = request.form.get('website_link')

      #venue seeking description
      venue_seeking_description = request.form.get('seeking_description')

      if venue_seeking_description : 
        venue_seeking_talent = True
      else:
        venue_seeking_talent = False

      #venue image
      venue_image_link = request.form.get('image_link')
      new_venue = Venue(name=venue_name , city=venue_city , state=venue_state , address=venue_address , phone=venue_phone , genres=venue_genres , facebook_link=venue_facebook_link , website=venue_website_link ,seeking_talent=venue_seeking_talent, seeking_description=venue_seeking_description , image_link=venue_image_link)
      db.session.add(new_venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      if error:
          # TODO: on unsuccessful db insert, flash an error instead.
          # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
          # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
          flash('An error occurred. Venue '+request.form['name']+ ' could not be Listed.')
      else:
          db.session.close()
          # on successful db insert, flash success
          flash('Venue ' + request.form['name'] + ' was successfully listed!')

    
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  current_venue = Venue.query.filter_by(id = venue_id).first()
  error = False
  try:
    db.session.delete(current_venue)
    db.session.commit()
  except:
    error =True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred . Venue '+current_venue.name+' could not be deleted because there is an Artist related to that venue')
    else:
      flash('Venue '+current_venue.name + ' was successfully deleted')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  all_artists = Artist.query.all()

  for artist in all_artists:
    data.append(
      {
        "id" : artist.id,
        "name" : artist.name
      }
    )


  #data=[{
  #  "id": 4,
  #  "name": "Guns N Petals",
  #}, {
  #  "id": 5,
  #  "name": "Matt Quevedo",
  #}, {
  #  "id": 6,
  #  "name": "The Wild Sax Band",
  #}]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searched_string = request.form.get('search_term')
  result = Artist.query.filter(Artist.name.ilike('%'+ searched_string+'%')).all()
  count = len(result)
  
  data=[]
  for artist in result:
    data.append({
      "id" : artist.id,
      "name" : artist.name,
      "num_upcoming_shows" : Show.c.venue_id,
    })
  response = {
    "count" : count,
    "data" : data
  }


  '''response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  '''
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  current_artist = Artist.query.filter_by(id=artist_id).first()
  past_shows = []
  upcoming_shows = []
  current_date = datetime.utcnow()
  #get all shows related to the current venue
  all_shows = db.session.query(Show).filter(Show.c.artist_id == Artist.id).all()
  for show in all_shows:
    #get the venue
    venue = Venue.query.filter_by(id=show.venue_id).first()
    if show.start_time >= current_date:
      upcoming_shows.append({
        "venue_id" : venue.id,
        "venue_name" :venue.name,
        "venue_image_link" : venue.image_link,
        "start_time": show.start_time
      })
    else:
      past_shows.append({
        "venue_id" : venue.id,
        "venue_name" :venue.name,
        "venue_image_link" : venue.image_link,
        "start_time": show.start_time
      })
  no_of_past_shows = len(past_shows)
  no_of_upcoming_shows = len(upcoming_shows)
  data = {
    "id": current_artist.id,
    "name": current_artist.name,
    "genres": current_artist.genres.split(','),
    "city": current_artist.city,
    "state": current_artist.state,
    "phone": current_artist.phone,
    "website": current_artist.website,
    "facebook_link": current_artist.facebook_link,
    "seeking_venue": current_artist.seeking_talent,
    "seeking_description":current_artist.seeking_description,
    "image_link": current_artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": no_of_past_shows,
    "upcoming_shows_count": no_of_upcoming_shows,
  }
  '''data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]'''
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  current_artist = Artist.query.filter_by(id = artist_id ).first()
  artist = {
    "id": current_artist.id,
    "name": current_artist.name,
    "genres": current_artist.genres,
    "city": current_artist.city,
    "state": current_artist.state,
    "phone": current_artist.phone,
    "website": current_artist.website,
    "facebook_link": current_artist.facebook_link,
    "seeking_venue": current_artist.seeking_talent,
    "seeking_description": current_artist.seeking_description,
    "image_link": current_artist.image_link
  }
  form.name.data = current_artist.name
  form.genres.data = current_artist.genres
  form.city.data = current_artist.city
  form.state.data = current_artist.state
  form.phone.data = current_artist.phone
  form.website_link.data = current_artist.website
  form.facebook_link.data = current_artist.facebook_link
  form.seeking_description.data = current_artist.seeking_description
  form.image_link.data = current_artist.image_link
  '''
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  '''
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  current_artist = Artist.query.filter_by(id = artist_id).first()

  error = False
  # get the data from the form
  
  try:
      #Artist name 
      current_artist.name = request.form.get('name')

      #Artist city and state
      current_artist.city = request.form.get('city')
      current_artist.state = request.form.get('state')

      #Artist phone
      current_artist.phone = request.form.get('phone')

      #Artist geners 
      current_artist_geners = request.form.getlist('genres')
      #construct your list [,,,]
      current_artist.genres = ','.join(current_artist_geners)

      #Artist facebook
      current_artist.facebook_link = request.form.get('facebook_link')

      #Artist website
      current_artist.websit = request.form.get('website_link')

      #Artist seeking description
      current_artist.seeking_description = request.form.get('seeking_description')
      if current_artist.seeking_description : 
        current_artist.seeking_talent = True
      else:
        current_artist.seeking_talent = False
      #Artist image
      current_artist.image_link = request.form.get('image_link')

      db.session.add(current_artist)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      if error:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      else:
          db.session.close()
          # on successful db update, flash success
          flash('Artist ' + request.form['name'] + ' was successfully Updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  current_venue = Venue.query.filter_by(id = venue_id ).first()
  venue = {
    "id": current_venue.id,
    "name": current_venue.name,
    "address" : current_venue.address,
    "genres": current_venue.genres,
    "city": current_venue.city,
    "state": current_venue.state,
    "phone": current_venue.phone,
    "website": current_venue.website,
    "facebook_link": current_venue.facebook_link,
    "seeking_venue": current_venue.seeking_talent,
    "seeking_description": current_venue.seeking_description,
    "image_link": current_venue.image_link
  }
  form.name.data = current_venue.name
  form.genres.data = current_venue.genres
  form.address.data = current_venue.address
  form.city.data = current_venue.city
  form.state.data = current_venue.state
  form.phone.data = current_venue.phone
  form.website_link.data = current_venue.website
  form.facebook_link.data = current_venue.facebook_link
  form.seeking_description.data = current_venue.seeking_description
  form.image_link.data = current_venue.image_link
 
  '''
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  '''
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  current_venue = Venue.query.filter_by(id = venue_id).first()
  error = False
  # get the data from the form
  
  try:
      #venue name 
      current_venue.name = request.form.get('name')

      #venue city and state
      current_venue.city = request.form.get('city')
      current_venue.state = request.form.get('state')

      #venue address
      current_venue.address = request.form.get('address')

      #venue phone
      current_venue.phone = request.form.get('phone')

      #venue geners 
      venue_genres = request.form.getlist('genres')
      #construct your list [,,,]
      current_venue.genres = ','.join(venue_genres)

      #venue facebook
      current_venue.facebook_link = request.form.get('facebook_link')

      #venue website
      current_venue.website_link = request.form.get('website_link')

      #venue seeking description
      current_venue.seeking_description = request.form.get('seeking_description')

      if current_venue.seeking_description : 
        current_venue.seeking_talent = True
      else:
        current_venue.seeking_talent = False

      #venue image
      current_venue.image_link = request.form.get('image_link')
      db.session.add(current_venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      if error:
          flash('An error occurred. Venue '+request.form['name']+ ' could not be Listed.')
      else:
          db.session.close()
          # on successful db update, flash success
          flash('Venue ' + request.form['name'] + ' was successfully listed!')

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
  # get the data from the form
  
  try:
      #Artist name 
      artist_name = request.form.get('name')

      #Artist city and state
      artist_city = request.form.get('city')
      artist_state = request.form.get('state')

      #Artist phone
      artist_phone = request.form.get('phone')

      #Artist geners 
      artist_genres = request.form.getlist('genres')
      #construct your list [,,,]
      artist_genres = ','.join(artist_genres)

      #Artist facebook
      artist_facebook_link = request.form.get('facebook_link')

      #Artist website
      artist_website_link = request.form.get('website_link')

      #Artist seeking description
      artist_seeking_description = request.form.get('seeking_description')
      if artist_seeking_description : 
        artist_seeking_talent = True
      else:
        artist_seeking_talent = False
      #Artist image
      artist_image_link = request.form.get('image_link')

      new_artist = Artist(name=artist_name , city=artist_city , state=artist_state , phone=artist_phone , genres=artist_genres , facebook_link=artist_facebook_link , website=artist_website_link ,seeking_talent=artist_seeking_talent, seeking_description=artist_seeking_description , image_link=artist_image_link)
      db.session.add(new_artist)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      
      if error:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      else:
          # on successful db insert, flash success
          flash('Artist ' + request.form['name'] + ' was successfully listed!')



  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #all_shows  = db.session.query(Show).all()
  all_shows  = db.session.query(Show).all()
  data=[]
  for show in all_shows:
    current_venue = Venue.query.filter_by(id = show.venue_id).first()
    current_artist = Artist.query.filter_by(id = show.artist_id).first()
    data.append({
      "venue_id" : show.venue_id,
      "venue_name" : current_venue.name,
      "artist_id" : show.artist_id,
      "artist_name" : current_artist.name,
      "artist_image_link" : current_artist.image_link,
      "start_time" : show.start_time
    })
  '''data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  '''
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
  try:

    show_artist_id = request.form.get('artist_id')

    show_venue_id = request.form.get('venue_id')

    show_start_time = request.form.get('start_time')

    new_show = Show.insert().values( venue_id=show_venue_id ,artist_id=show_artist_id , start_time=show_start_time )
    db.session.execute(new_show)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        flash('An error occurred. Show could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

 
  
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
