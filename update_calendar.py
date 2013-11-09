# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import sys
import MovieFetcher
import datetime

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

from prettytable import PrettyTable

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/966749676004/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def get_service():
    """Returns a service object used to interact with the calendar."""
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    flags = parser.parse_args(sys.argv[1:])
    if credentials is None or credentials.invalid:
      credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = discovery.build('calendar', 'v3', http=http)
    return service

def get_calendars(service):
    """Returns a list of calenders, each represented by a dictionary."""
    return service.calendarList().list().execute()['items']

def get_table(fields):
    table=PrettyTable(field_names=fields)
    for key in table.align:
        table.align[key] = "l"
    return table

def print_calendars(fields=[u'id', u'description', u'summary', u'timeZone']):
    """Prints a the key features of a calendar list."""
    service=get_service()
    calendars=get_calendars(service)

    table=get_table(fields)

    for cal in calendars:
        row=[]
        for field in fields:
            row.append(cal.get(field, None))
        table.add_row(row)
    print table

def get_events(calendarId):
    service=get_service()
    return service.events().list(calendarId=calendarId, maxResults=5000).execute()['items']

def print_events(calendarId):
    events=get_events(calendarId)
    fields=[u'id', u'summary', u'start', u'end']
    table=PrettyTable(field_names=fields)
    for key in table.align:
        table.align[key] = "l"
    for event in events:
        row=[]
        for field in fields:
            row.append(event.get(field, None))
        table.add_row(row)
    print table

def delete_events(service, calendar_id):
    for event in get_events(calendar_id):
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()


def main(argv):
  # Parse the command-line flags.
  #flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  #storage = file.Storage('sample.dat')
  #credentials = storage.get()
  #if credentials is None or credentials.invalid:
  #  credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  #http = httplib2.Http()
  #http = credentials.authorize(http)

  # Construct the service object for the interacting with the Calendar API.
  #service = discovery.build('calendar', 'v3', http=http)
  service=get_service()

  try:
    #for item in service.calendarList().list().execute()["items"]:
    #    print item['summary'], item['id']

    tarbut_calendar_id="matan.name_8hnqrrn9h5e6ijkunlfkjetj9s@group.calendar.google.com"
    sderot_calendar_id="matan.name_55j9srv12aamsve51u2vvm9cuk@group.calendar.google.com"
    #events=service.events().list(calendarId=tarbut_calendar_id).execute()
    #for event in events['items']:
    #    print event['summary'], event.keys()

    #print service.events().quickAdd(calendarId=sderot_calendar_id, text="Seret at Sderot! November 5th, 2013 13:00-14:00", sendNotifications=None).execute()
    #print get_calendars(service)
    #print_calendars()
    schedule=MovieFetcher.Schedule()

    #for screening in schedule.screenings:

     #   print screening
        #
        #event = {
        #    'summary': screening.movie.title,
        #    'location': 'הדגל 4, שדרות, ישראל',
        #    'description': screening.movie.description,
        #    'start': {
        #        'dateTime': screening.date.strftime("%Y-%m-%dT%H:%M:%S.000+02:00") #2011-06-03T10:00:00.000-07:00
        #    },
        #    'end': {
        #        'dateTime': (screening.date+datetime.timedelta(0, screening.movie.duration*60)).strftime("%Y-%m-%dT%H:%M:%S.00+02:00")
        #    },
        #
        #    }
        #
        #print event
        #created_event = service.events().insert(calendarId=sderot_calendar_id, body=event).execute()

    print_events(sderot_calendar_id)

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)

