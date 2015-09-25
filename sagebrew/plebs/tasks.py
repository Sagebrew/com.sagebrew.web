import us
from uuid import uuid1

from django.core import signing
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.cache import cache

from elasticsearch import Elasticsearch, NotFoundError

from boto.ses.exceptions import SESMaxSendingRateExceededError
from celery import shared_task

from py2neo.cypher import ClientError
from neomodel import DoesNotExist, CypherException, db

from api.utils import spawn_task, generate_oauth_user
from api.tasks import add_object_to_search_index
from sb_base.utils import defensive_exception
from sb_wall.neo_models import Wall

from sb_registration.models import token_gen
from sb_privileges.tasks import check_privileges
from sb_locations.neo_models import Location

from .neo_models import Pleb, BetaUser, OauthUser, Address
from .utils import create_friend_request_util


@shared_task()
def pleb_user_update(username, first_name, last_name, email):
    from .serializers import PlebSerializerNeo
    pleb = cache.get(username)
    if pleb is None:
        try:
            pleb = Pleb.nodes.get(username=username)
        except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
            raise pleb_user_update.retry(exc=e, countdown=3, max_retries=None)

    try:
        pleb.first_name = first_name
        pleb.last_name = last_name
        pleb.email = email

        pleb.save()
        pleb.update_campaign()
        pleb.refresh()
        cache.set(pleb.username, pleb)
        document = PlebSerializerNeo(pleb).data
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            es.delete(index="full-search-base",
                      doc_type=document['type'], id=document['id'])
        except NotFoundError:
            pass
        es.index(index="full-search-base", doc_type=document['type'],
                 id=document['id'], body=document)
    except(CypherException, IOError) as e:
        raise pleb_user_update.retry(exc=e, countdown=3, max_retries=None)

    return True


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
        result = determine_reps(username)
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
                '(d:Location {name:"%s"}) RETURN d' % \
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
def finalize_citizen_creation(user_instance=None):
    from .serializers import PlebSerializerNeo
    # TODO look into celery chaining and/or grouping
    if user_instance is None:
        return None
    username = user_instance.username
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise finalize_citizen_creation.retry(exc=e, countdown=3,
                                              max_retries=None)
    task_list = {}
    task_data = {
        "object_uuid": pleb.object_uuid,
        'object_data': PlebSerializerNeo(pleb).data
    }
    task_list["add_object_to_search_index"] = spawn_task(
        task_func=add_object_to_search_index,
        task_param=task_data,
        countdown=30)
    task_list["check_privileges_task"] = spawn_task(
        task_func=check_privileges, task_param={"username": username},
        countdown=20)
    if not pleb.initial_verification_email_sent:
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
    task_ids = []
    cache.set(pleb.username, pleb)
    for item in task_list:
        task_ids.append(task_list[item].task_id)
    return task_list


@shared_task()
def create_wall_task(user_instance=None):
    if user_instance is None:
        return None
    try:
        pleb = Pleb.nodes.get(username=user_instance.username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise create_wall_task.retry(exc=e, countdown=3, max_retries=None)
    try:
        wall_list = pleb.wall.all()
    except(CypherException, IOError) as e:
        raise create_wall_task.retry(exc=e, countdown=3, max_retries=None)
    if len(wall_list) > 1:
        return False
    elif len(wall_list) == 1:
        pass
    else:
        try:
            wall = Wall(wall_id=str(uuid1())).save()
            wall.owned_by.connect(pleb)
            pleb.wall.connect(wall)
        except(CypherException, IOError) as e:
            raise create_wall_task.retry(exc=e, countdown=3,
                                         max_retries=None)
    spawned = spawn_task(task_func=finalize_citizen_creation,
                         task_param={"user_instance": user_instance})
    if isinstance(spawned, Exception) is True:
        raise create_wall_task.retry(exc=spawned, countdown=3,
                                     max_retries=None)
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
def create_pleb_task(user_instance=None, birthday=None, password=None):
    # We do a check to make sure that a user with the email given does not exist
    # in the registration view, so if you are calling this function without
    # using that view there is a potential UniqueProperty error which can get
    # thrown.
    if user_instance is None:
        return None
    try:
        Pleb.nodes.get(username=user_instance.username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise create_pleb_task.retry(exc=e, countdown=3, max_retries=None)
    except(CypherException, IOError) as e:
        raise create_pleb_task.retry(exc=e, countdown=3, max_retries=None)
    task_info = spawn_task(task_func=create_wall_task,
                           task_param={"user_instance": user_instance})
    if isinstance(task_info, Exception) is True:
        raise create_pleb_task.retry(exc=task_info, countdown=3,
                                     max_retries=None)
    oauth_res = spawn_task(task_func=generate_oauth_info,
                           task_param={'username': user_instance.username,
                                       'password': password},
                           countdown=20)
    if isinstance(oauth_res, Exception):
        raise create_pleb_task.retry(exc=oauth_res, countdown=3,
                                     max_retries=None)
    return task_info


@shared_task()
def create_beta_user(email):
    try:
        BetaUser.nodes.get(email=email)
        return True
    except (BetaUser.DoesNotExist, DoesNotExist):
        beta_user = BetaUser(email=email)
        beta_user.save()
    except (CypherException, IOError) as e:
        raise create_beta_user.retry(exc=e, countdown=3, max_retries=None)
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
        pleb = Pleb.get(username=username)
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
        pleb.refresh()
        cache.set(username, pleb)
        if isinstance(check_priv, Exception):
            raise update_reputation.retry(exc=check_priv, countdown=3,
                                          max_retries=None)
    return True
