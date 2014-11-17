from uuid import uuid1
from json import dumps
from boto.ses.exceptions import SESMaxSendingRateExceededError
from celery import shared_task
from logging import getLogger
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from sb_base.utils import defensive_exception
from sb_search.tasks import add_user_to_custom_index
from sb_wall.neo_models import SBWall
from sb_registration.models import token_gen

from .neo_models import Pleb

logger = getLogger('loggly_logs')


@shared_task()
def send_email_task(to, subject, html_content, text_content=None):
    # TODO do we need text content here?
    # Also if not make sure to remove it from finalize_citizen_creation
    from sb_registration.utils import sb_send_email
    try:
        res = sb_send_email(to, subject, html_content)
        if isinstance(res, Exception):
            raise send_email_task.retry(exc=res, countdown=5, max_retries=None)
    except SESMaxSendingRateExceededError as e:
        raise send_email_task.retry(exc=e, countdown=5,
                                    max_retries=None)
    except Exception as e:
        raise defensive_exception(send_email_task.__name__, e,
                                  send_email_task.retry(exc=e, countdown=3,
                                                        max_retries=None))


@shared_task()
def finalize_citizen_creation(pleb, user):
    # TODO look into celery chaining and/or grouping
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
    task_data = {'pleb': pleb,
                 'index': "full-search-user-specific-1"}
    task_list["add_user_to_custom_index"] = spawn_task(
        task_func=add_user_to_custom_index,
        task_param=task_data)

    if not pleb.initial_verification_email_sent:
        generated_token = token_gen.make_token(user, pleb)
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
def create_wall_task(pleb, user):
    try:
        if len(pleb.wall.all()) == 1:
            return spawn_task(task_func=finalize_citizen_creation,
                              task_param={"pleb": pleb, "user": user})
        elif len(pleb.wall.all()) > 1:
            return False
        wall = SBWall(wall_id=str(uuid1())).save()
        wall.owner.connect(pleb)
        pleb.wall.connect(wall)
        return spawn_task(task_func=finalize_citizen_creation,
                          task_param={"pleb": pleb, "user": user})
    except (TypeError, CypherException) as e:
        raise create_wall_task.retry(exc=e, countdown=3,
                                     max_retries=None)
    except Exception as e:
        raise defensive_exception(create_wall_task.__name__, e,
                                  create_wall_task.retry(exc=e, countdown=3,
                                                         max_retries=None))


@shared_task()
def create_pleb_task(user_instance):
    try:
        try:
            test = Pleb.nodes.get(email=user_instance.email)
            return spawn_task(create_wall_task,
                              task_param={'pleb': test, 'user': user_instance})
        except (Pleb.DoesNotExist, DoesNotExist):
            pleb = Pleb(email=user_instance.email,
                        first_name=user_instance.first_name,
                        last_name=user_instance.last_name)
            pleb.save()
            pleb.generate_username()
            task_info = spawn_task(task_func=create_wall_task,
                              task_param={"pleb": pleb, "user": user_instance})
            return task_info
    except CypherException as e:
        raise create_pleb_task.retry(exc=e, countdown=3,
                                     max_retries=None)
    except Exception as e:
        raise defensive_exception(create_pleb_task.__name__, e,
                                  create_pleb_task.retry(exc=e, countdown=3,
                                                         max_retries=None))
