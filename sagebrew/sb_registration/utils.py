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


def generate_address_tuple(address_info):
    address_tuple = ()
    choice = 0
    for address_choice in address_info:
        if("address2" in address_choice):
            address_string = "%s, %s, %s, %s %s" % (address_choice["street"],
                                                address_choice["street_additional"],
                                                address_choice["city"],
                                                address_choice["state"],
                                                address_choice["postal_code"])
        else:
            address_string = "%s, %s, %s %s" % (address_choice["street"],
                                                address_choice["city"],
                                                address_choice["state"],
                                                address_choice["postal_code"])
        address_tuple = address_tuple + ((choice, address_string),)
        choice += 1

    return address_tuple

def validate_address(address_request):
    '''
    This function validates the address given to it in the form of a dict. The dict
    contains fields which smartystreets requires to validate an address. If the address
    is valid it returns 1 and if not it fails.
    '''
    LOCATION = 'https://api.smartystreets.com/street-address/'#move to settings
    auth_id = '84a98057-05ed-4109-8758-19acd5336c38'
    auth_token = 'p3GbchbjA3q13MUdT7gM'
    address_request['auth-id'] = auth_id
    address_request['auth-token'] = auth_token
    address_request['street'] = address_request['primary_address']
    address_request.pop('primary_address', None)
    address_request['zipCode'] = address_request['postal_code']
    address_request.pop('postal_code', None)
    QUERY_STRING = urllib.urlencode(address_request)

    URL = LOCATION + '?' + QUERY_STRING

    response = urllib.urlopen(URL).read()
    structure = json.loads(response)
    array_of_addresses = []

    # TODO Tyler check this for loop
    for address in structure:
        address_dict = {"street": address["delivery_line_1"],
                        "city": address["components"]["city_name"],
                        "state": address["components"]["state_abbreviation"],
                        "postal_code": address["components"]["zipcode"],
                        "congressional_district":
                            address["metadata"]["congressional_district"],
                        "latitude": address["metadata"]["latitude"],
                        "longitude": address["metadata"]["longitude"]}
        if("delivery_line_2" in address):
            address_dict["street_additional"] = address["delivery_line_2"]
        else:
            address_dict["street_additional"] = None
        array_of_addresses.append(address_dict)

    return array_of_addresses


def compare_address(smarty_address, address_clean):
    temp_smarty = smarty_address.copy()
    temp_address = address_clean.copy()
    temp_smarty.pop("longitude", None)
    temp_smarty.pop("congressional_district", None)
    temp_smarty.pop("latitude", None)
    if(temp_address["street_additional"] == ""):
        temp_address["street_additional"] = None

    temp_address.pop("country", None)
    temp_address["postal_code"] = temp_address.pop("zipCode", None)
    temp_address.pop("auth-token", None)
    temp_address.pop("auth-id", None)
    print temp_smarty
    print temp_address
    print smarty_address
    print address_clean
    print temp_smarty == temp_address
    return temp_smarty == temp_address




def upload_image(folder_name, file_uuid):
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
    print "finished upload"
    return image_uri