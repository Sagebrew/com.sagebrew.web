import us
import requests
from uuid import uuid1

from django.core import signing
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.cache import cache
from django.contrib.auth.models import User

from boto.ses.exceptions import SESMaxSendingRateExceededError
from celery import shared_task

from py2neo.cypher.error.transaction import ClientError, CouldNotCommit
from neomodel import DoesNotExist, CypherException, db

from api.utils import spawn_task, generate_oauth_user
from sb_search.tasks import update_search_object
from sb_base.utils import defensive_exception
from sb_public_official.tasks import create_and_attach_state_level_reps
from sb_registration.models import token_gen
from sb_privileges.tasks import check_privileges
from sb_locations.neo_models import Location

from .neo_models import Pleb, OauthUser, Address
from .utils import create_friend_request_util


@shared_task()
def send_email_task(source, to, subject, html_content):
    from sb_registration.utils import sb_send_email
    try:
        res = sb_send_email(source, to, subject, html_content)
        if isinstance(res, Exception):
            raise send_email_task.retry(exc=res, countdown=5, max_retries=None)
    except SESMaxSendingRateExceededError as e:
        raise send_email_task.retry(exc=e, countdown=5, max_retries=None)
    except Exception as e:
        raise defensive_exception(send_email_task.__name__, e,
                                  send_email_task.retry(exc=e, countdown=3,
                                                        max_retries=None))


@shared_task()
def determine_pleb_reps(username):
    from sb_public_official.utils import determine_reps
    try:
        pleb = Pleb.nodes.get(username=username)
        result = determine_reps(pleb)
        if result is False:
            raise Exception("Failed to determine reps")
        return result
    except Exception as e:
        raise determine_pleb_reps.retry(exc=e, countdown=3, max_retries=None)


@shared_task()
def update_address_location(object_uuid):
    try:
        address = Address.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Address.DoesNotExist, CypherException, IOError,
            ClientError) as e:
        raise update_address_location.retry(exc=e, countdown=3,
                                            max_retries=None)
    try:
        state = us.states.lookup(address.state)
        district = address.congressional_district
        query = 'MATCH (a:Address {object_uuid:"%s"})-[r:ENCOMPASSED_BY]->' \
                '(l:Location) DELETE r' % object_uuid
        db.cypher_query(query)
        query = 'MATCH (s:Location {name:"%s"})-[:ENCOMPASSES]->' \
                '(d:Location {name:"%s", sector:"federal"}) RETURN d' % \
                (state, district)
        res, _ = db.cypher_query(query)
        if res.one is not None:
            district = Location.inflate(res.one)
            district.addresses.connect(address)
            address.encompassed_by.connect(district)
        address.set_encompassing()
    except (CypherException, IOError, ClientError) as e:
        raise update_address_location.retry(exc=e, countdown=3,
                                            max_retries=None)
    return True


@shared_task()
def connect_to_state_districts(object_uuid):
    try:
        address = Address.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Address.DoesNotExist, CypherException, IOError,
            ClientError) as e:
        raise connect_to_state_districts.retry(exc=e, countdown=3,
                                               max_retries=None)
    try:
        lookup_url = settings.OPENSTATES_DISTRICT_SEARCH_URL % \
            (address.latitude, address.longitude) \
            + "&apikey=53f7bd2a41df42c082bb2f07bd38e6aa"
    except TypeError:
        # in case an address doesn't have a latitude or longitude
        return False
    response = requests.get(
        lookup_url, headers={"content-type": 'application/json; charset=utf8'})
    response_json = response.json()
    try:
        for rep in response_json:
            try:
                sector = 'state_%s' % rep['chamber']
                query = 'MATCH (l:Location {name: "%s", sector:"federal"})-' \
                        '[:ENCOMPASSES]->(district:Location {name:"%s", ' \
                        'sector:"%s"}) RETURN district ' % \
                        (us.states.lookup(address.state).name,
                         rep['district'], sector)
                res, _ = db.cypher_query(query)
            except KeyError:
                return False
            try:
                res = res[0]
            except IndexError as e:
                raise connect_to_state_districts.retry(exc=e, countdown=3,
                                                       max_retries=None)
            try:
                state_district = Location.inflate(res.district)
            except (CypherException, ClientError, IOError, CouldNotCommit) as e:
                raise connect_to_state_districts.retry(exc=e, countdown=3,
                                                       max_retries=None)
            if state_district not in address.encompassed_by:
                address.encompassed_by.connect(state_district)
            if address not in state_district.addresses:
                state_district.addresses.connect(address)
        spawn_task(task_func=create_and_attach_state_level_reps,
                   task_param={"rep_data": response_json})
        return True
    except (CypherException, IOError, ClientError, CouldNotCommit) as e:
        raise connect_to_state_districts.retry(exc=e, countdown=3,
                                               max_retries=None)


@shared_task()
def finalize_citizen_creation(username):
    # TODO look into celery chaining and/or grouping
    res, _ = db.cypher_query("MATCH (a:Pleb {username:'%s'}) RETURN a" %
                             username)
    if res.one:
        res.one.pull()
        pleb = Pleb.inflate(res.one)
    else:
        raise finalize_citizen_creation.retry(
            exc=DoesNotExist('Profile with username: %s '
                             'does not exist' % username), countdown=3,
            max_retries=None)
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
    if not pleb.initial_verification_email_sent:
        user_instance = User.objects.get(username=username)
        generated_token = token_gen.make_token(user_instance, pleb)
        template_dict = {
            'full_name': user_instance.get_full_name(),
            'verification_url': "%s%s/" % (settings.EMAIL_VERIFICATION_URL,
                                           generated_token)
        }
        subject, to = "Sagebrew Email Verification", pleb.email
        html_content = get_template(
            'email_templates/email_verification.html').render(
            Context(template_dict))
        task_dict = {
            "to": to, "subject": subject,
            "html_content": html_content, "source": "support@sagebrew.com"
        }
        task_list["send_email_task"] = spawn_task(
            task_func=send_email_task, task_param=task_dict)
        if task_list['send_email_task'] is not None:
            pleb.initial_verification_email_sent = True
            pleb.save()
    cache.delete(pleb.username)
    return task_list


@shared_task()
def create_wall_task(username=None):
    try:
        query = 'MATCH (pleb:Pleb {username: "%s"})' \
                '-[:OWNS_WALL]->(wall:Wall) RETURN wall' % username
        res, _ = db.cypher_query(query)
        if not res.one:
            query = 'MATCH (pleb:Pleb {username: "%s"}) ' \
                    'CREATE UNIQUE (pleb)-[:OWNS_WALL]->' \
                    '(wall:Wall {wall_id: "%s"}) ' \
                    'RETURN wall' % (username, str(uuid1()))
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
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
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
def create_friend_request_task(from_username, to_username, object_uuid):
    res = create_friend_request_util(from_username, to_username, object_uuid)
    if isinstance(res, Exception):
        return create_friend_request_task.retry(exc=res, countdown=3,
                                                max_retries=None)
    return res


@shared_task()
def update_reputation(username):
    try:
        pleb = Pleb.nodes.get(username=username)
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
