from logging import getLogger
from uuid import uuid1

from django.core import signing
from django.core.cache import cache

from celery import shared_task

from py2neo.cypher.error.transaction import ClientError
from neomodel import DoesNotExist, CypherException, db

from api.utils import spawn_task, generate_oauth_user
from sb_search.tasks import update_search_object
from sb_privileges.tasks import check_privileges

from .neo_models import Pleb, OauthUser

logger = getLogger('loggly_logs')


@shared_task()
def determine_pleb_reps(username):
    from sb_public_official.utils import determine_reps
    try:
        pleb = Pleb.get(username=username, cache_buster=True)
        result = determine_reps(pleb)
        if result is False:
            raise Exception("Failed to determine reps")
        return result
    except Exception as e:
        raise determine_pleb_reps.retry(exc=e, countdown=3, max_retries=None)


@shared_task()
def finalize_citizen_creation(username):
    try:
        pleb = Pleb.get(username=username, cache_buster=True)
    except (DoesNotExist, Exception) as e:
        raise finalize_citizen_creation.retry(
            exc=e, countdown=10, max_retries=None)
    task_list = {}
    task_data = {
        "object_uuid": pleb.object_uuid,
        "label": "pleb"
    }
    task_list["add_object_to_search_index"] = spawn_task(
        task_func=update_search_object,
        task_param=task_data,
        countdown=30)
    task_list["check_privileges_task"] = spawn_task(
        task_func=check_privileges, task_param={"username": username},
        countdown=20)

    cache.delete(pleb.username)
    return task_list


@shared_task()
def create_wall_task(username=None):
    from sb_wall.neo_models import Wall
    try:
        query = 'MATCH (pleb:Pleb {username: "%s"})' \
                '-[:OWNS_WALL]->(wall:Wall) RETURN wall' % username
        res, _ = db.cypher_query(query)
        if res.one is None:
            wall = Wall(wall_id=str(uuid1())).save()
            query = 'MATCH (pleb:Pleb {username: "%s"}),' \
                    '(wall:Wall {wall_id: "%s"}) ' \
                    'CREATE UNIQUE (pleb)-[:OWNS_WALL]->(wall) ' \
                    'RETURN wall' % (username, wall.wall_id)
            res, _ = db.cypher_query(query)
        spawned = spawn_task(task_func=finalize_citizen_creation,
                             task_param={"username": username})
        if isinstance(spawned, Exception) is True:
            raise create_wall_task.retry(exc=spawned, countdown=3,
                                         max_retries=None)
    except (CypherException, IOError, ClientError) as e:
        raise create_wall_task.retry(exc=e, countdown=3, max_retries=None)
    return spawned


@shared_task
def generate_oauth_info(username, password, web_address=None):
    try:
        pleb = Pleb.get(username=username, cache_buster=True)
    except (DoesNotExist, CypherException, IOError) as e:
        raise generate_oauth_info.retry(exc=e, countdown=3, max_retries=None)
    creds = generate_oauth_user(pleb, password, web_address)

    if isinstance(creds, Exception):
        raise generate_oauth_info.retry(exc=creds, countdown=3,
                                        max_retries=None)
    try:
        oauth_obj = OauthUser(access_token=signing.dumps(creds['access_token']),
                              token_type=creds['token_type'],
                              expires_in=creds['expires_in'],
                              refresh_token=signing.dumps(
                                  creds['refresh_token']))
        oauth_obj.save()
    except(CypherException, IOError) as e:
        return e

    try:
        pleb.oauth.connect(oauth_obj)
    except(CypherException, IOError) as e:
        return e

    return True


@shared_task()
def update_reputation(username):
    try:
        pleb = Pleb.get(username=username, cache_buster=True)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise update_reputation.retry(exc=e, countdown=3, max_retries=None)

    res = pleb.get_total_rep()
    if isinstance(res, Exception):
        raise update_reputation.retry(exc=res, countdown=3, max_retries=None)
    if res['previous_rep'] != res['total_rep']:
        pleb.reputation_update_seen = False
        pleb.save()
        check_priv = spawn_task(task_func=check_privileges,
                                task_param={"username": username})
        cache.delete(username)
        if isinstance(check_priv, Exception):
            raise update_reputation.retry(exc=check_priv, countdown=3,
                                          max_retries=None)
    return True
