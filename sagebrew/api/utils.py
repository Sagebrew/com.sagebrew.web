import logging
import requests
from uuid import uuid1
from socket import error as socket_error
from json import loads, dumps
from django.conf import settings
from requests import post as request_post
from django.contrib.auth.models import User
from provider.oauth2.models import Client as OauthClient
import boto.sqs
from boto.sqs.message import Message
from bomberman.client import Client
from neomodel.exception import CypherException
from neomodel import db

from api.alchemyapi import AlchemyAPI
from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost
from sb_garbage.neo_models import SBGarbageCan


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
    '''
    try:
        attempt_task.apply_async([info,], countdown=countdown, task_id=task_id)
    except socket_error:
    '''
    conn = boto.sqs.connect_to_region(
        "us-west-2",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    my_queue = conn.get_queue('sb_failures')
    m = Message()
    m.set_body(dumps(message_info))
    my_queue.write(m)


def spawn_task(task_func, task_param, countdown=0, task_id=str(uuid1())):
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
        logger.error(dumps(
            {'failure_uuid': failure_uuid, 'function': task_func.__name__,
             'exception': 'socket_error'}))
        logger.exception('Trace back from error: ')
        add_failure_to_queue(failure_dict)
        return False
    except Exception:
        failure_uuid = str(uuid1())
        failure_dict = {
            'action': 'failed_task',
            'attempted_task': task_func.__name__,
            'task_info_kwargs': task_param,
            'failure_uuid': failure_uuid
        }
        logger.error(dumps(
            {'failure_uuid': failure_uuid, 'function': task_func.__name__,
             'exception': 'unknown_error'}))
        logger.exception('Trace back from error: ')
        add_failure_to_queue(failure_dict)
        return False


def get_post_data(request):
    '''
    used when dealing with data from an ajax call or from a regular post.
    determines whether to get the data from request.DATA or request.body

    :param request:
    :return:
    '''
    post_info = loads(request.body)
    if not post_info:
        try:
            post_info = request.DATA
        except ValueError:
            return {}
    return post_info


def language_filter(content):
    '''
    Filters harsh language from posts and comments using the bomberman
    client which
    is initialized each time the function is called.

    :param content:
    :return:
    '''
    bomberman = Client()
    if bomberman.is_profane(content):
        corrected_content = bomberman.censor(content)
        return corrected_content
    else:
        return content


def post_to_garbage(post_id):
    try:
        post = SBPost.nodes.get(post_id=post_id)
        query = 'MATCH (p:SBPost) WHERE p.post_id="%s" ' \
                'WITH p MATCH (p) - [:HAS_A] - (c:SBComment) ' \
                'WHERE c.to_be_deleted=False ' \
                'WITH c ORDER BY c.created_on ' \
                'RETURN c' % post.post_id
        comments, meta = execute_cypher_query(query)
        comments = [SBComment.inflate(row[0]) for row in comments]
        for comment in comments:
            comment.to_be_deleted = True
            comment.save()
        garbage_can = SBGarbageCan.nodes.get(garbage_can='garbage')
        post.to_be_deleted = True
        garbage_can.posts.connect(post)
        garbage_can.save()
        post.save()
    except SBGarbageCan.DoesNotExist:
        post = SBPost.nodes.get(post_id=post_id)
        garbage_can = SBGarbageCan(garbage_can='garbage')
        garbage_can.save()
        post.to_be_deleted = True
        garbage_can.posts.connect(post)
        garbage_can.save()
        post.save()
    except SBPost.DoesNotExist:
        pass


def comment_to_garbage(comment_id):
    try:
        comment = SBComment.nodes.get(comment_id=comment_id)
        garbage_can = SBGarbageCan.nodes.get(garbage_can='garbage')
        comment.to_be_deleted = True
        garbage_can.comments.connect(comment)
        garbage_can.save()
        comment.save()
    except SBGarbageCan.DoesNotExist:
        comment = SBComment.nodes.get(comment_id=comment_id)
        garbage_can = SBGarbageCan(garbage_can='garbage')
        garbage_can.save()
        comment.to_be_deleted = True
        garbage_can.comments.connect(comment)
        garbage_can.save()
        comment.save()
    except SBComment.DoesNotExist:
        pass


def create_auto_tags(content):
    alchemyapi = AlchemyAPI()
    keywords = alchemyapi.keywords("text", content)
    return keywords


def execute_cypher_query(query):

    try:
        return db.cypher_query(query)
    except CypherException:
        logger.exception("CypherException: ")
        return {'detail': 'CypherException'}
    except Exception, e:
        logger.exception("UnhandledException: ")
        return {'detail': 'fail'}


def clear_neodb():
    try:
        db.cypher_query("START n=node(*) MATCH n-[r?]-() DELETE r,n")
    except CypherException:
        pass
