from uuid import uuid1
from boto.ses.exceptions import SESMaxSendingRateExceededError
from celery import shared_task
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from sb_base.utils import defensive_exception
from sb_search.tasks import add_user_to_custom_index
from sb_wall.neo_models import SBWall
from sb_docstore.tasks import add_object_to_table_task
from sb_registration.models import token_gen

from .neo_models import Pleb

@shared_task()
def send_email_task(to, subject, html_content, text_content=None):
    from sb_registration.utils import sb_send_email
    try:
        res = sb_send_email(to, subject, html_content)
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
            'pleb_email': pleb.email
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
    if not pleb.initial_verification_email_sent:
        generated_token = token_gen.make_token(user_instance, pleb)
        template_dict = {
            'full_name': "%s %s" % (pleb.first_name, pleb.last_name),
            'verification_url': "%s%s/" % (settings.EMAIL_VERIFICATION_URL,
                                           generated_token)
        }
        subject, to = "Sagebrew Email Verification", pleb.email
        text_content = get_template(
            'email_templates/email_verification.txt').render(
            Context(template_dict))
        html_content = get_template(
            'email_templates/email_verification.html').render(
            Context(template_dict))
        task_dict = {
            "to": to, "subject": subject, "text_content": text_content,
            "html_content": html_content
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
def create_pleb_task(user_instance=None):
    if user_instance is None:
        return None
    try:
        pleb = Pleb.nodes.get(email=user_instance.email)
    except (Pleb.DoesNotExist, DoesNotExist):
        try:
            pleb = Pleb(email=user_instance.email,
                        first_name=user_instance.first_name,
                        last_name=user_instance.last_name)
            # TODO do we need this save or can we use the one in
            # generate_username?
            pleb.save()
        except(CypherException, IOError) as e:
            raise create_pleb_task.retry(exc=e, countdown=3, max_retries=None)
    except(CypherException, IOError) as e:
        raise create_pleb_task.retry(exc=e, countdown=3, max_retries=None)
    if pleb.username is None:
        generated = pleb.generate_username(user_instance)
        if isinstance(generated, Exception):
            raise create_pleb_task.retry(exc=generated, countdown=3,
                                         max_retries=None)
    task_info = spawn_task(task_func=create_wall_task,
                           task_param={"user_instance": user_instance})
    if isinstance(task_info, Exception) is True:
        raise create_pleb_task.retry(exc=task_info, countdown=3,
                                     max_retries=None)
    return task_info
