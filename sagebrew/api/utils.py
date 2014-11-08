import logging
import time
import boto.sqs
import importlib

from uuid import uuid1
from socket import error as socket_error
from json import dumps

from boto.sqs.message import Message
from bomberman.client import Client, RateLimitExceeded
from neomodel.exception import CypherException, DoesNotExist
from neomodel import db
from django.conf import settings

from api.alchemyapi import AlchemyAPI
from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost

logger = logging.getLogger('loggly_logs')

'''
# TOOD Add tagging process into git so that we can label point that we deleted
this
def post_to_api(api_url, data, headers=None):
    if headers is None:
        headers = {}
    headers['Authorization'] = "Bearer %s" % (get_oauth_access_token())
    url = "%s%s" % (settings.WEB_ADDRESS, api_url)
    response = request_post(url, data=dumps(data),
                            verify=settings.VERIFY_SECURE, headers=headers)
    return response.json()


def get_oauth_client():
    url = settings.WEB_ADDRESS + '/oauth2/access_token'
    user = User.objects.get(username="admin")
    client = OauthClient.objects.get(user=1)
    response = requests.post(url, data={
        'client_id': client.client_id,
        'client_secret': client.client_secret,
        'username': user.username,
        'password': settings.API_PASSWORD,
        'grant_type': 'password'}, verify=settings.VERIFY_SECURE)
    return response.json()


def refresh_oauth_access_token(oauth_client):
    url = settings.WEB_ADDRESS + '/oauth2/access_token'
    data = {
        'client_id': oauth_client['client_id'],
        'client_secret': oauth_client['client_secret'],
        'grant_type': 'refresh_token',
        'refresh_token': oauth_client['refresh_token']
    }
    response = requests.post(url, data=data,
                             verify=settings.VERIFY_SECURE)
    return response


def check_oauth_expires_in(oauth_client):
    if oauth_client['expires_in'] < 100:
        return True
    return False


def get_oauth_access_token():
    oauth_client = get_oauth_client()
    if check_oauth_expires_in(oauth_client):
        return refresh_oauth_access_token(oauth_client)['access_token']
    return oauth_client['access_token']



iron_mq = IronMQ(project_id=settings.IRON_PROJECT_ID,
                         token=settings.IRON_TOKEN)
        queue = iron_mq.queue('sb_failures')
        info['action'] = attempt_task.__name__
        queue.post(dumps(info))
'''


#TODO if add_failure_to_queue fails store in postgress database in a meta field
#allow for backup if Amazon goes down
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


def spawn_task(task_func, task_param, countdown=0, task_id=None):
    if task_id is None:
        task_id = str(uuid1())
    try:
        return task_func.apply_async(kwargs=task_param, countdown=countdown,
                                     task_id=task_id)
    except socket_error:
        failure_uuid = str(uuid1())
        failure_dict = {
            'action': 'failed_task',
            'attempted_task': task_func.__name__,
            'task_info_kwargs': task_param,
            'failure_uuid': failure_uuid
        }
        logger.exception(dumps(
            {'failure_uuid': failure_uuid, 'function': task_func.__name__,
             'exception': 'socket_error'}))
        add_failure_to_queue(failure_dict)
        return None
    except Exception:
        failure_uuid = str(uuid1())
        failure_dict = {
            'action': 'failed_task',
            'attempted_task': task_func.__name__,
            'task_info_kwargs': task_param,
            'failure_uuid': failure_uuid
        }
        logger.exception(dumps(
            {'failure_uuid': failure_uuid, 'function': task_func.__name__,
             'exception': 'Unhandled Exception'}))
        add_failure_to_queue(failure_dict)
        return None


def language_filter(content):
    '''
    Filters harsh language from posts and comments using the bomberman
    client which
    is initialized each time the function is called.

    :param content:
    :return:
    '''
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
    # TODO Improve exception handling and change related functions accordingly
    try:
        alchemyapi = AlchemyAPI()
        keywords = alchemyapi.keywords("text", content)
        return keywords
    except Exception:
        logger.exception(dumps({"function": create_auto_tags,
                                "exception": "Unhandled Exception"}))
        return None


def execute_cypher_query(query):
    try:
        return db.cypher_query(query)
    except CypherException:
        return {'detail': 'CypherException'}
    except Exception:
        logger.exception(dumps({"function": execute_cypher_query.__name__,
                                "exception":"Unhandled Exception"}))
        return {'detail': 'fail'}


def test_wait_util(async_res):
    while not async_res['task_id'].ready():
        time.sleep(1)

    while not async_res['task_id'].result.ready():
        time.sleep(1)


def get_object(object_type, object_uuid):
    '''
    DO NOT USE THIS FUNCTION ANYWHERE THAT DOES NOT HAVE A FORM
    AND A CHOICE FIELD CLEARLY LAID OUT.

    This function will take the id of an object and the objects class
    name as a string: SBPost: "SBPost", etc. and return the object.
    If the object is not found it will return False

    :param object_type:
    :param object_uuid:
    :return:
    '''
    try:
        cls = object_type
        print cls
        module_name, class_name = cls.rsplit(".", 1)
        sb_module = importlib.import_module(module_name)
        sb_object = getattr(sb_module, class_name)
        try:
            return sb_object.nodes.get(sb_id=object_uuid)
        except (sb_object.DoesNotExist, DoesNotExist) as e:
            return TypeError("%s.DoesNotExist"%object_type)
    except (CypherException, NameError) as e:
        return e
    except Exception as e:
        logger.exception(dumps({"function": get_object.__name__,
                                "exception": "Unhandled Exception"}))
        return e

