from uuid import uuid1
from time import strptime
from boto.ses.exceptions import SESMaxSendingRateExceededError
from celery import shared_task
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from sb_base.utils import defensive_exception
from sb_search.tasks import add_user_to_custom_index
from sb_wall.neo_models import SBWall
from sb_docstore.tasks import add_object_to_table_task
from sb_registration.models import token_gen
from sb_privileges.tasks import check_privileges

from .neo_models import Pleb, BetaUser

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
def finalize_citizen_creation(user_instance=None):
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
        'object_added': pleb,
        'object_data': {
            'first_name': pleb.first_name,
            'last_name': pleb.last_name,
            'full_name': "%s %s" % (pleb.first_name, pleb.last_name),
            'pleb_email': pleb.email,
            'object_uuid': pleb.username
            },
        'object_type': 'pleb'
    }
    task_list["add_object_to_search_index"] = spawn_task(
        task_func=add_object_to_search_index,
        task_param=task_data)
    task_data = {'username': username,
                 'index': "full-search-user-specific-1"}
    task_list["add_user_to_custom_index"] = spawn_task(
        task_func=add_user_to_custom_index,
        task_param=task_data)
    dynamo_data = {'table': 'users_barebones', 'object_data':
        {'email': pleb.email,
         'first_name': pleb.first_name,
         'last_name': pleb.last_name,
         'username': pleb.username,
         'type': 'standard'}}
    task_list["add_object_to_table_task"] = spawn_task(
        task_func=add_object_to_table_task, task_param=dynamo_data)
    task_list["check_privileges_task"] = spawn_task(
        task_func=check_privileges, task_param={"username": username})
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
            wall = SBWall(wall_id=str(uuid1())).save()
            wall.owner.connect(pleb)
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


@shared_task()
def create_pleb_task(user_instance=None, birthday=None):
    #We do a check to make sure that a user with the email given does not exist
    #in the registration view, so if you are calling this function without
    #using that view there is a potential UniqueProperty error which can get
    #thrown.
    if user_instance is None:
        return None
    try:
        pleb = Pleb.nodes.get(username=user_instance.username)
    except (Pleb.DoesNotExist, DoesNotExist):
        try:
            pleb = Pleb(email=user_instance.email,
                        first_name=user_instance.first_name,
                        last_name=user_instance.last_name,
                        username=user_instance.username,
                        birthday=birthday)
            pleb.save()
        except(CypherException, IOError) as e:
            raise create_pleb_task.retry(exc=e, countdown=3, max_retries=None)
    except(CypherException, IOError) as e:
        raise create_pleb_task.retry(exc=e, countdown=3, max_retries=None)
    task_info = spawn_task(task_func=create_wall_task,
                           task_param={"user_instance": user_instance})
    if isinstance(task_info, Exception) is True:
        raise create_pleb_task.retry(exc=task_info, countdown=3,
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
    except CypherException as e:
        raise create_beta_user.retry(exc=e, countdown=3, max_retries=None)
    return True

@shared_task()
def deactivate_user_task(username):
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        raise deactivate_user_task.retry(exc=e, countdown=3, max_retries=None)

