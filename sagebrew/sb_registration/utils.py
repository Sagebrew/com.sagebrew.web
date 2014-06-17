from plebs.neo_models import TopicCategory
import json
import urllib
import httplib2

from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.shortcuts import render_to_response as render
from django.utils.html import escape
import gdata.contacts.service
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from apiclient.discovery import build

GOOGLE_CONTACTS_URI = 'http://www.google.com/m8/feeds/'

def generate_interests_tuple():
    cat_instance = TopicCategory.category()
    categories = cat_instance.instance.all()
    # For reasoning behind tuples here look at
    # http://stackoverflow.com/questions/15210511/solved-django-modelchoicefield-optgroup-tag/17854288#17854288
    # We are basically able to draw on django's built in categorization of
    # choices rather then implementing a bunch of custom logic
    sb_topic_choices = ()
    choices_tuple = ()
    for category in categories:
        for item in category.sb_topics.all():
            sb_topic_choices = sb_topic_choices + ((item.title, item.title),)
        category_tuple = (category.title, sb_topic_choices)
        sb_topic_choices = ()
        choices_tuple = choices_tuple + (category_tuple,)

    return choices_tuple

def validate_address(addressrequest):
    LOCATION = 'https://api.smartystreets.com/street-address/'#move to settings
    auth_id = '84a98057-05ed-4109-8758-19acd5336c38'
    auth_token = 'p3GbchbjA3q13MUdT7gM'
    addressrequest['auth-id']=auth_id
    addressrequest['auth-token']=auth_token
    addressrequest['street']=addressrequest['primary_address']
    addressrequest.pop('primary_address',None)
    addressrequest['zipCode']=addressrequest['postal_code']
    addressrequest.pop('postal_code',None)
    QUERY_STRING = urllib.urlencode(addressrequest)

    URL = LOCATION + '?' + QUERY_STRING

    response = urllib.urlopen(URL).read()
    structure = json.loads(response)
    if structure:
        return 1


def get_google_contact_emails():
    flow = OAuth2WebServerFlow(client_id='993581225427-32f6in1htts4sdmcduaq6oeg29c7iib3.apps.googleusercontent.com',
                               client_secret='9cLhnm0PhNNlRQivNUqnHo0J',
                               scope=GOOGLE_CONTACTS_URI,
                               redirect_uri='http://192.168.56.101/auth_return/')
    auth_uri = flow.step1_get_authorize_url()
    redirect(auth_uri)
    code = auth_uri.replace('http://example.com/auth_return/?code=','')
    credentials = flow.step2_exchange(code)
    storage = Storage(credentials)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('contacts', 'v3', http=http)
    '''ontacts_service = gdata.contacts.service.ContactsService()
    contacts_service.auth_token = authsub_token
    contacts_service.UpgradeToSessionToken()
    emails = []
    feed = contacts_service.GetContactsFeed()
    emails.extend(sum([[email.address for email in entry.email] for entry in feed.entry], []))
    next_link = feed.GetNextLink()
    while next_link:
        feed = contacts_service.GetContactsFeed(uri=next_link.href)
        emails.extend(sum([[email.address for email in entry.email] for entry in feed.entry], []))
        next_link = feed.GetNextLink()'''

