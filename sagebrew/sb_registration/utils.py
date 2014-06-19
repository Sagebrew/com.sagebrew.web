import os
from plebs.neo_models import TopicCategory
import json
import urllib
from django.conf import settings
from boto import connect_s3
from boto.s3.key import Key
from uuid import uuid1



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

'''
This function validates the address given to it in the form of a dict. The dict
contains fields which smartystreets requires to validate an address. If the address
is valid it returns 1 and if not it fails.
'''
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


def upload_image(folder_name,file_uuid):
    file_path = '%s%s.%s' % (settings.TEMP_FILES, file_uuid, 'jpeg')
    print file_path
    bucket = settings.AWS_UPLOAD_BUCKET_NAME
    conn = connect_s3(settings.AWS_UPLOAD_CLIENT_KEY,
                      settings.AWS_UPLOAD_CLIENT_SECRET_KEY)
    k = Key(conn.get_bucket(bucket))
    k.key = "%s/%s.%s" % (folder_name, file_uuid, "jpeg")
    k.set_contents_from_filename(file_path)
    k.make_public()
    image_uri = k.generate_url(expires_in=100000)
    os.remove(file_path)
    return image_uri