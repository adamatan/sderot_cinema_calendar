#!/usr/bin/python

import urllib2
import json
import datetime
import re

class Screening():
    def __init__(self, screening_dict, movies):
        properties=screening_dict['propertyMap']
        self.movie_id = int(properties['movieId'])
        self.movie    = movies[self.movie_id]
        self.theatre  = properties['theater']
        self.date     = datetime.datetime.strptime(properties['date'], "%b %d, %Y %I:%M:%S %p")

    def __str__(self):
        return json.dumps({"id":self.movie_id, "date":str(self.date), "theater":self.theatre, "duration":self.movie.duration})

class Movie():
    def __init__(self, movies_dict):
        properties          = movies_dict['propertyMap']
        self.title          = properties['title']
        self.movie_id       = int(properties['movieId'])
        try:
            self.duration = int(re.match("\d+", properties['duration']).group(0))
        except:
            self.duration = 120
        try:
            self.description    = properties['description']['value']['value']
        except TypeError:
            self.description    = properties['description']

    def __str__(self):
        return json.dumps({"title":self.title, "id":self.movie_id, "duration":self.duration})


full_schedule=json.loads(urllib2.urlopen("http://cinema-sderot.appspot.com/getSchedule").read())


movies      =   [Movie(movies_dict) for movies_dict in full_schedule['movies']]
movies      = { movie.movie_id:movie for movie in movies }
screenings  =   [Screening(screening_dict, movies) for screening_dict in full_schedule['screenings']]