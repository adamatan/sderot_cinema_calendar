#!/usr/bin/python

import urllib2
import json
import datetime
import re
from prettytable import PrettyTable

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

class Schedule():
    def __init__(self):
        self.schedule   = json.loads(urllib2.urlopen("http://cinema-sderot.appspot.com/getSchedule").read())
        self.movies     = [Movie(movies_dict) for movies_dict in self.schedule['movies']]
        self.movies     = { movie.movie_id:movie for movie in self.movies }
        self.screenings = [Screening(screening_dict, self.movies) for screening_dict in self.schedule['screenings']]

if __name__=='__main__':
    schedule=Schedule()
    table=PrettyTable(field_names=["date", "duration", "theater", "name"])
    table.align['name']='r'
    for screening in schedule.screenings:
        table.add_row((screening.date, screening.movie.duration, screening.theatre, screening.movie.title))

    print table