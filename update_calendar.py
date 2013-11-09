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

def print_events(events):
    fields=[u'id', u'summary', u'start', u'end']
    table=PrettyTable(field_names=fields)
    for key in table.align:
        table.align[key] = "l"
    for event in events:
        row=[event['id'], event['summary'], event['start']['dateTime'], event['end']['dateTime']]
        table.add_row(row)
    print table

def datestring_to_datetime(datestring):
    return datetime.datetime.strptime(datestring.split("+")[0], "%Y-%m-%dT%H:%M:%S")

def delete_events(service, calendar_id):
    for event in get_events(calendar_id):
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()

def create_event(screening):
    title_prepend = u"שדרות: "
    event = {
        'summary': title_prepend+screening.movie.title,
        'location': 'הדגל 4, שדרות, ישראל',
        'description': screening.movie.description,
        'start': {
            'dateTime': screening.date.strftime("%Y-%m-%dT%H:%M:%S.000+02:00")
        },
        'start.timeZone' : "Jerusalem/Israel",
        'end.timeZone'   : "Jerusalem/Israel",
        'end': {
            'dateTime': (screening.date+datetime.timedelta(0, screening.movie.duration*60)).strftime("%Y-%m-%dT%H:%M:%S.00+02:00")
        },

        }
    return event

def delete_and_rebuild_calendar(calendar_id):
    service=get_service()
    schedule=MovieFetcher.Schedule()
    delete_events(service, calendar_id)
    for screening in schedule.screenings:
        service.events().insert(calendarId=calendar_id, body=create_event(screening)).execute()

def find_event_for_screening(events, screening):
    for event in events:
        event_time=datestring_to_datetime(event.get('start')['dateTime'])
        if event_time==screening.date and event.get("description")==screening.movie.description:
            return event.get("id")
    return None

def update_calendar(calendar_id):
    service=get_service()
    schedule=MovieFetcher.Schedule()
    events_already_in_calendar=get_events(calendar_id)
    print_events(events_already_in_calendar)

    for screening in schedule.screenings:
        event_id=find_event_for_screening(events_already_in_calendar, screening)
        event=create_event(screening)
        if event_id:
            print "Updating!"
            service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        else:
            service.events().insert(calendarId=calendar_id, body=screening).execute()


def main(argv):
  service=get_service()

  try:
    sderot_calendar_id="matan.name_55j9srv12aamsve51u2vvm9cuk@group.calendar.google.com"
    update_calendar(sderot_calendar_id)

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)

