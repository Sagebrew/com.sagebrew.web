import os
import shortuuid
import hashlib
import boto.ses
from boto.ses.exceptions import SESMaxSendingRateExceededError
from datetime import date
from django.conf import settings
from django.contrib.auth.models import User

from boto import connect_s3
from boto.s3.key import Key
from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from plebs.tasks import create_pleb_task
from plebs.neo_models import Pleb
from sb_base.decorators import apply_defense



def calc_age(birthday):
    '''
    This function just calculates and returns the age of a person based on
    given date.

    :param birthday:
    :return:
    '''
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day)
                                         < (birthday.month - birthday.day))


def create_address_long_hash(address):
    if "street_additional" in address:
        address_string = "%s%s%s%s%s%s%f%f%s" % (address["primary_address"],
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
        address_string = "%s%s%s%s%s%f%f%s" % (address["primary_address"],
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

"""
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
"""


def validate_school(school_name):
    pass


def upload_image(folder_name, file_uuid, file_location=None):
    '''
    Creates a connection to the s3 service then uploads the file which was
    passed
    to this function an uses the uuid as the filename.

    :param folder_name:
    :param file_uuid:
    :return:
    '''
    if file_location is None:
        file_path = '%s%s.%s' % (settings.TEMP_FILES, file_uuid, 'jpg')
    else:
        file_path = '%s%s.%s' % (file_location, file_uuid, 'jpg')

    bucket = settings.AWS_STORAGE_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))
    key_string = "%s/%s.%s" % (folder_name, file_uuid, "jpg")
    k.key = key_string
    k.set_contents_from_filename(file_path)
    image_uri = k.generate_url(expires_in=259200)
    if os.environ.get("CIRCLECI", "false") == "false":
        os.remove(file_path)
    return image_uri


def generate_profile_pic_url(image_uuid):
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))
    key_string = "%s/%s.%s" % (settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                               image_uuid, "jpeg")
    k.key = key_string
    image_uri = k.generate_url(expires_in=259200)
    return image_uri

"""
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
"""


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
        return pleb.completed_profile_info
    except (Pleb.DoesNotExist, DoesNotExist, CypherException):
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
    except CypherException as e:
        return e

@apply_defense
def sb_send_email(to_email, subject, html_content):
    '''
    This function is used to send mail through the amazon ses service,
    we can use this for any emails we send just specify html content

    :param to_email:
    :param subject:
    :param html_content:
    :return:
    '''
    try:
        conn = boto.ses.connect_to_region(
            'us-east-1',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        conn.send_email(source='devon@sagebrew.com', subject=subject,
                        body=html_content, to_addresses=[to_email],
                        format='html')
        return True
    except SESMaxSendingRateExceededError as e:
        return e

@apply_defense
def create_user_util(first_name, last_name, email, password, username=None):
    if username is None:
        username = str(shortuuid.uuid())
    user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                    email=email, password=password,
                                    username=username)
    user.save()
    res = spawn_task(task_func=create_pleb_task,
                     task_param={"user_instance": user})
    if isinstance(res, Exception) is True:
        return res
    else:
        return {"task_id": res, "username": user.username}
