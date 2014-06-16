from plebs.neo_models import TopicCategory
import json
import urllib
import pprint


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
    LOCATION = 'https://api.smartystreets.com/street-address/'
    auth_id = '84a98057-05ed-4109-8758-19acd5336c38'
    auth_token = 'p3GbchbjA3q13MUdT7gM'
    addressrequest['auth-id']=auth_id
    addressrequest['auth-token']=auth_token
    addressrequest['street']=addressrequest['Primary Address*']
    addressrequest.pop('Primary Address',None)
    addressrequest['city']=addressrequest['City*']
    addressrequest.pop('City*',None)
    addressrequest['state']=addressrequest['State*']
    addressrequest.pop('State*',None)
    addressrequest['zipCode']=addressrequest['Postal Code*']
    addressrequest.pop('Postal Code*',None)
    QUERY_STRING = urllib.urlencode(addressrequest)

    URL = LOCATION + '?' + QUERY_STRING

    response = urllib.urlopen(URL).read()
    structure = json.loads(response)
    pprint.pprint(structure)

