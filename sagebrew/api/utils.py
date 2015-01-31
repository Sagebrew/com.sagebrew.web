import time
import pytz
import boto.sqs
import importlib
import requests
import hashlib
import shortuuid
from uuid import uuid1
from json import dumps
from datetime import timedelta, datetime
from django.core import signing
from django.contrib.auth.models import User
from boto.sqs.message import Message
from bomberman.client import Client, RateLimitExceeded
from neomodel import db
from neomodel.exception import CypherException, DoesNotExist

from django.conf import settings

from sb_base.utils import defensive_exception
from sb_base.decorators import apply_defense
from plebs.neo_models import Pleb, OauthUser
from api.alchemyapi import AlchemyAPI



def post_to_api(api_url, data, username, headers=None):
    if headers is None:
        headers = {}
    headers['Authorization'] = "%s %s" % (get_oauth_access_token(username))
    url = "%s%s" % (settings.WEB_ADDRESS, api_url)
    response = requests.post(url, data=dumps(data),
                            verify=settings.VERIFY_SECURE, headers=headers)
    return response.json()


def get_oauth_client(username, password, web_address, client_id=None,
                     client_secret=None):
    if client_id is None:
        client_id = settings.OAUTH_CLIENT_ID
    if client_secret is None:
        client_secret = settings.OAUTH_CLIENT_SECRET
    response = requests.post(web_address, data={
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password,
        'grant_type': 'password'}, verify=settings.VERIFY_SECURE)
    return response.json()


def refresh_oauth_access_token(refresh_token, url, client_id=None,
                               client_secret=None):
    if client_id is None:
        client_id = settings.OAUTH_CLIENT_ID
    if client_secret is None:
        client_secret = settings.OAUTH_CLIENT_SECRET
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(url, data=data,
                             verify=settings.VERIFY_SECURE)
    return response.json()


def check_oauth_expires_in(oauth_client):
    elapsed = datetime.now(pytz.utc) - oauth_client.last_modified
    if elapsed.total_seconds() < 1800:
        return True
    return False


def get_oauth_access_token(username, web_address=None):
    if web_address is None:
        web_address = settings.WEB_ADDRESS + '/o/token/'
    pleb = Pleb.nodes.get(username=username)
    try:
        oauth_creds = [oauth_user for oauth_user in pleb.oauth.all()
                  if oauth_user.web_address == web_address][0]
    except IndexError:
        return
    if check_oauth_expires_in(oauth_creds):
        refresh_token = decrypt(oauth_creds.refresh_token)
        updated_creds = refresh_oauth_access_token(refresh_token,
                                          oauth_creds.web_address)
        oauth_creds.last_modified = datetime.now(pytz.utc)
        oauth_creds.access_token = encrypt(updated_creds['access_token'])
        oauth_creds.token_type = updated_creds['token_type']
        oauth_creds.expires_in = updated_creds['expires_in']
        oauth_creds.refresh_token = encrypt(updated_creds['refresh_token'])
        oauth_creds.save()

    return decrypt(oauth_creds.access_token)

def generate_oauth_user(username, password, web_address=None):
    if web_address is None:
        web_address = settings.WEB_ADDRESS + '/o/token/'
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    creds = get_oauth_client(username, password, web_address)
    try:
        oauth_obj = OauthUser(access_token=encrypt(creds['access_token']),
                          token_type=creds['token_type'],
                          expires_in=creds['expires_in'],
                          refresh_token=encrypt(creds['refresh_token'])).save()
    except CypherException as e:
        return e
    try:
        pleb.oauth.connect(oauth_obj)
    except CypherException as e:
        return e
    return True

def encrypt(data):
    return signing.dumps(data)

def decrypt(data):
    return signing.loads(data)

def generate_short_token():
    short_hash = hashlib.sha1(shortuuid.uuid())
    short_hash.update(settings.SECRET_KEY)
    return short_hash.hexdigest()[::2]

def generate_long_token():
    long_hash = hashlib.sha1(shortuuid.uuid())
    long_hash.update(settings.SECRET_KEY)
    return long_hash.hexidigest()

'''
# TODO Add tagging process into git so that we can label point that we deleted this
iron_mq = IronMQ(project_id=settings.IRON_PROJECT_ID,
                         token=settings.IRON_TOKEN)
        queue = iron_mq.queue('sb_failures')
        info['action'] = attempt_task.__name__
        queue.post(dumps(info))
'''

def add_failure_to_queue(message_info):
    conn = boto.sqs.connect_to_region(
        "us-west-2",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    my_queue = conn.get_queue('sb_failures')
    m = Message()
    m.set_body(dumps(message_info))
    my_queue.write(m)
    return True


def spawn_task(task_func, task_param, countdown=0, task_id=None):
    if task_id is None:
        task_id = str(uuid1())
    try:
        return task_func.apply_async(kwargs=task_param, countdown=countdown,
                                     task_id=task_id)
    except (IOError, Exception) as e:
        failure_uuid = str(uuid1())
        failure_dict = {
            'action': 'failed_task',
            'attempted_task': task_func.__name__,
            'task_info_kwargs': task_param,
            'failure_uuid': failure_uuid
        }
        add_failure_to_queue(failure_dict)
        return defensive_exception(spawn_task.__name__, e, e,
            {"failure_uuid": failure_uuid, "failure": "Unhandled Exception"})


def language_filter(content):
    """
    Filters harsh language from posts and comments using the bomberman
    client which
    is initialized each time the function is called.

    :param content:
    :return:
    """
    try:
        bomberman = Client()
        if bomberman.is_profane(content):
            corrected_content = bomberman.censor(content)
            return corrected_content
        else:
            return content
    except RateLimitExceeded:
        return False


def create_auto_tags(content):
    try:
        alchemyapi = AlchemyAPI()
        keywords = alchemyapi.keywords("text", content)
        return keywords
    except Exception as e:
        return defensive_exception(create_auto_tags.__name__, e, e)


def wait_util(async_res):
    while not async_res['task_id'].ready():
        time.sleep(1)

    while not async_res['task_id'].result.ready():
        time.sleep(1)
    return async_res['task_id'].result.result


@apply_defense
def get_object(object_type, object_uuid):
    """
    DO NOT USE THIS FUNCTION ANYWHERE THAT DOES NOT HAVE A FORM
    AND A CHOICE FIELD CLEARLY LAID OUT.

    This function will take the id of an object and the objects class
    name as a string: SBPost: "SBPost", etc. and return the object.
    If the object is not found it will return False

    :param object_type:
    :param object_uuid:
    :return:
    """
    try:
        cls = object_type
        module_name, class_name = cls.rsplit(".", 1)
        sb_module = importlib.import_module(module_name)
        sb_object = getattr(sb_module, class_name)
        try:
            return sb_object.nodes.get(sb_id=object_uuid)
        except (sb_object.DoesNotExist, DoesNotExist):
            return TypeError("%s.DoesNotExist" % object_type)
    except (NameError, ValueError, ImportError, AttributeError):
        return False
    except CypherException as e:
        return e


def execute_cypher_query(query):
    try:
        return db.cypher_query(query)
    except(CypherException, IOError) as e:
        return e