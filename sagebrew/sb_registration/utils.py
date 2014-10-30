import os
import shortuuid
import hashlib
import json
import urllib
import boto.ses
import logging
from boto.ses.exceptions import SESMaxSendingRateExceededError
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


def validate_school(school_name):
    pass

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
        return pleb.completed_profile_info
    except (Pleb.DoesNotExist,DoesNotExist):
        return False
    except CypherException:
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
    try:
        conn = boto.ses.connect_to_region(
            'us-east-1',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        )

        conn.send_email(source='devon@sagebrew.com',
                        subject=subject,
                        body=html_content,
                        to_addresses=[to_email],
                        format='html')
        return True
    except SESMaxSendingRateExceededError as e:
        return e
    except Exception as e:
        logger.exception(json.dumps({"function": sb_send_email.__name__,
                                     "exception": "UnhandledException: "}))
        return e

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
            logger.critical(json.dumps({"function": create_user_util.__name__,
                          "exception": "res is None"}))
            return False
    except Exception:
        logger.exception(json.dumps({"function": create_user_util.__name__,
                          "exception": "UnhandledException: "}))
        return False
