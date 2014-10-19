import os
import shortuuid
import hashlib
import json
import urllib
import boto.ses
import logging
from socket import error as socket_error
from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
from boto import connect_s3
from boto.s3.key import Key
from neomodel import DoesNotExist, CypherException
from api.utils import spawn_task
from plebs.tasks import create_pleb_task
from plebs.neo_models import TopicCategory, Pleb
from govtrack.neo_models import GTRole

logger = logging.getLogger('loggly_logs')

def generate_interests_tuple():
    cat_instance = TopicCategory.category()
    categories = cat_instance.instance.all()
    # For reasoning behind tuples here look at
    # http://stackoverflow.com/questions/15210511/solved-django
    # -modelchoicefield-optgroup-tag/17854288#17854288
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

def calc_age(birthday):
    '''
    This function just calculates and returns the age of a person based on
    given date.

    :param birthday:
    :return:
    '''
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month - birthday.day))

def create_address_long_hash(address):
    if ("address2" in address):
        address_string = "%s%s%s%s%s%s%f%f%s" % (address["street"],
                                                 address["street_additional"],
                                                 address["city"],
                                                 address["state"],
                                                 address["postal_code"],
                                                 address["country"],
                                                 address["latitude"],
                                                 address["longitude"],
                                                 address[
                                                     "congressional_district"])
    else:
        address_string = "%s%s%s%s%s%f%f%s" % (address["street"],
                                               address["city"],
                                               address["state"],
                                               address["postal_code"],
                                               address["country"],
                                               address["latitude"],
                                               address["longitude"],
                                               address[
                                                   "congressional_district"])
    address_hash = hashlib.sha224(address_string).hexdigest()

    return address_hash


def create_address_string(address):
    if ("address2" in address):
        address_string = "%s, %s, %s, %s %s" % (address["street"],
                                                address["street_additional"],
                                                address["city"],
                                                address["state"],
                                                address["postal_code"])
    else:
        address_string = "%s, %s, %s %s" % (address["street"], address["city"],
                                            address["state"],
                                            address["postal_code"])

    return address_string


def generate_address_tuple(address_info):
    '''
    COMPLETED THIS TASK BUT STILL NEED TO PUT SOME COMMENTS AROUND IT
    Need to use a hash to verify the same address string is being
    used instead of an int. That way if smarty streets passes back
    the addresses in a different order we can use the same address
    we provided the user previously based on the previous
    smarty streets ordering.
    We should hash the entire string and use that as the choice field
    since choices only allows strings with no white space.

    The integer process currently being used leaves room for a bug to appear
    if smarty streets returns the addresses in a different order after the
    user has picked an address from the initial list smarty streets provided.
    This can happen because we rely on smarty streets to reprovide a list
    of the same addresses to enable us to validate the POST data provided
    by the user after receiving the address_selection_form due to
    invalidated addresses.
    :param address_info:
    :return:
    '''
    address_tuple = ()
    for address_choice in address_info:
        address_string = create_address_string(address_choice)
        address_hash = hashlib.sha224(address_string).hexdigest()
        address_tuple = address_tuple + ((address_hash, address_string),)

    return address_tuple


def validate_address(address_request):
    '''
    This function validates the address given to it in the form of a dict.
    The dict
    contains fields which smartystreets requires to validate an address. If
    the address
    is valid it returns 1 and if not it fails.
    '''
    # TODO figure out alternative with buggy addresses
    #127 glenwood dr walled lake mi 48390
    LOCATION = 'https://api.smartystreets.com/street-address/'  #move to
    # settings
    auth_id = settings.ADDRESS_VALIDATION_ID
    auth_token = settings.ADDRESS_VALIDATION_TOKEN
    address_request['auth-id'] = auth_id
    address_request['auth-token'] = auth_token
    address_request['street'] = address_request['primary_address']
    address_request.pop('primary_address', None)
    address_request['zipCode'] = address_request['postal_code']
    address_request.pop('postal_code', None)
    QUERY_STRING = urllib.urlencode(address_request)

    URL = LOCATION + '?' + QUERY_STRING
    response = urllib.urlopen(URL).read()
    try:
        structure = json.loads(response)
    except ValueError:
        return False

    return create_address_array(structure)


def validate_school(school_name):
    pass


def create_address_array(structure):
    array_of_addresses = []
    for address in structure:
        address_dict = {"street": address["delivery_line_1"],
                        "city": address["components"]["city_name"],
                        "state": address["components"]["state_abbreviation"],
                        "postal_code": address["components"]["zipcode"],
                        "congressional_district":
                            address["metadata"]["congressional_district"],
                        "latitude": address["metadata"]["latitude"],
                        "longitude": address["metadata"]["longitude"]}
        if ("delivery_line_2" in address):
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
    if (temp_address["street_additional"] == ""):
        temp_address["street_additional"] = None

    temp_address.pop("country", None)
    temp_address["postal_code"] = temp_address.pop("zipCode", None)
    temp_address.pop("auth-token", None)
    temp_address.pop("auth-id", None)

    return temp_smarty == temp_address


def upload_image(folder_name, file_uuid):
    '''
    Creates a connection to the s3 service then uploads the file which was
    passed
    to this function an uses the uuid as the filename.

    :param folder_name:
    :param file_uuid:
    :return:
    '''
    file_path = '%s%s.%s' % (settings.TEMP_FILES, file_uuid, 'jpeg')

    bucket = settings.AWS_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))
    key_string = "%s/%s.%s" % (folder_name, file_uuid, "jpeg")
    k.key = key_string
    k.set_contents_from_filename(file_path)
    image_uri = k.generate_url(expires_in=259200)
    os.remove(file_path)
    return image_uri

def generate_profile_pic_url(image_uuid):
    bucket = settings.AWS_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))
    key_string = "%s/%s.%s" % (settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                               image_uuid, "jpeg")
    k.key = key_string
    image_uri = k.generate_url(expires_in=259200)
    return image_uri


def determine_senators(pleb_address):
    '''
    Search for senators who match the state of the pleb. Then return an
    array of them

    :param pleb_address:
    :return:
    '''
    determined_sen = []
    senator_names = []
    senator_names = ['There are no senators in the DB']
    senator_array = GTRole.index.search(state=pleb_address.state, title='Sen.')
    for senator in senator_array:
        determined_sen.append(senator.person.all())
    for item in determined_sen:
        for name in item:
            senator_names.append(name.name)
    return senator_names


def determine_reps(pleb_address):
    '''
    Search for House Representatives who match the state and district of the
    pleb
    :param pleb_address:
    :return:
    '''
    determined_reps = []
    rep_name = 'There are no representatives in the DB'
    rep_array = GTRole.index.search(state=pleb_address.state, title='Rep.',
                                    district=int(
                                        pleb_address.congressional_district))
    for rep in rep_array:
        determined_reps.append(rep.person.all())
    for item in determined_reps:
        for name in item:
            rep_name = name.name
    return rep_name


def get_friends(email):
    '''
    Creates a list of dictionaries which hold data about the friends of the
    user

    :param email:
    :return:
    '''
    try:
        citizen = Pleb.nodes.get(email=email)
    except (Pleb.DoesNotExist, DoesNotExist):
        return []
    friends = []
    friends_list = citizen.friends.all()

    for friend in friends_list:
        friend_dict = {'name': friend.first_name + ' ' + friend.last_name,
                       'email': friend.email, 'picture': friend.profile_pic}
        friends.append(friend_dict)

    return friends

def verify_completed_registration(user):
    '''
    This function checks if the user has complete registration, it is used
    in the user_passes_test decorator

    :param user:
    :return:
    '''
    try:
        pleb = Pleb.nodes.get(email=user.email)
        logger.critical({"complete_profile_info": pleb.completed_profile_info})
        return pleb.completed_profile_info
    except (Pleb.DoesNotExist,DoesNotExist):
        logger.critical({"exception": "Pleb does not exist",
                         "function": "verify_completed_registration"})
        return False
    except CypherException:
        logger.critical({"exception": "cypher exception",
                         "function": "verify_completed_registration"})
        return False

def verify_verified_email(user):
    '''
    This function checks if the user has verified their email address,
    It is used in the user_passes_test decorator

    :param user:
    :return:
    '''
    try:
        pleb = Pleb.nodes.get(email=user.email)
        return pleb.email_verified
    except (Pleb.DoesNotExist, DoesNotExist):
        return False
    except CypherException:
        logger.critical({"exception": "cypher exception",
                         "function": "verify_verified_email"})
        return False

def sb_send_email(to_email, subject, text_content, html_content):
    '''
    This function is used to send mail through the amazon ses service,
    we can use this for any emails we send just specify html content

    :param to_email:
    :param subject:
    :param text_content:
    :param html_content:
    :return:
    '''
    conn = boto.ses.connect_to_region(
        'us-east-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    )

    res = conn.send_email(source='devon@sagebrew.com',
                          subject=subject,
                          body=html_content,
                          to_addresses=[to_email],
                          format='html')

def create_user_util(first_name, last_name, email, password,
                     username=""):
    try:
        if username == "":
            username = shortuuid.uuid()
        user = User.objects.create_user(first_name=first_name,
                                        last_name=last_name,
                                        email=email,
                                        password=password,
                                        username=username)
        user.save()
        res = spawn_task(task_func=create_pleb_task,
                         task_param={"user_instance": user})
        if res is not None:
            return {"task_id": res, "username": user.username}
        else:
            return False
    except Exception:
        logger.exception({"function": create_user_util.__name__,
                          "exception": "UnhandledException: "})
        return False
