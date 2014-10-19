from uuid import uuid1
from json import dumps
from celery import shared_task
from logging import getLogger
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from neomodel import DoesNotExist, CypherException

from .neo_models import Pleb
from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from sb_search.tasks import add_user_to_custom_index
from sb_wall.neo_models import SBWall
from sb_registration.models import EmailAuthTokenGenerator

logger = getLogger('loggly_logs')


@shared_task()
def send_email_task(to, subject, text_content, html_content):
    from sb_registration.utils import sb_send_email
    try:
        sb_send_email(to, subject, text_content, html_content)
    except Exception:
        logger.exception(dumps({"function": send_email_task.__name__,
                                "exception": "Unhandled Exception"}))
        raise send_email_task.retry(exc=Exception, countdown=3,
                                    max_retries=None)


@shared_task()
def create_pleb_task(user_instance):
    # TODO review with Tyler
    token_gen = EmailAuthTokenGenerator()
    try:
        try:
            test = Pleb.nodes.get(email=user_instance.email)
            logger.critical({"function": "create_pleb_task",
                             "pleb_email": test.email,
                             "pleb": test})
            return False
        except (Pleb.DoesNotExist, DoesNotExist):
            pleb = Pleb(email=user_instance.email,
                        first_name=user_instance.first_name,
                        last_name=user_instance.last_name)
            pleb.save()
            wall = SBWall(wall_id=str(uuid1()))
            wall.save()
            wall.owner.connect(pleb)
            pleb.wall.connect(wall)
            wall.save()
            pleb.save()

            task_data = {'object_data': {
                    'first_name': pleb.first_name,
                    'last_name': pleb.last_name,
                    'full_name': str(pleb.first_name) + ' '
                                 + str(pleb.last_name),
                    'pleb_email': pleb.email
                    },
                             'object_type': 'pleb'
                }
            spawn_task(task_func=add_object_to_search_index,
                           task_param=task_data)
            task_data = {'pleb': pleb.email,
                         'index': "full-search-user-specific-1"}
            spawn_task(task_func=add_user_to_custom_index,
                       task_param=task_data)
            generated_token = token_gen.make_token(user_instance, pleb)

            template_dict = {
                'full_name': "%s %s" % (pleb.first_name, pleb.last_name),
                'verification_url': "%s%s/" % (settings.EMAIL_VERIFICATION_URL,
                                               generated_token)
            }
            subject, to = "Sagebrew Email Verification", pleb.email
            text_content = get_template(
                'email_templates/email_verification.txt').\
                render(Context(template_dict))
            html_content = get_template(
                'email_templates/email_verification.html').\
                render(Context(template_dict))
            task_dict = {
                "to": to, "subject": subject, "text_content": text_content,
                "html_content": html_content
            }
            spawn_task(task_func=send_email_task, task_param=task_dict)
            return True
    except DoesNotExist:
        raise create_pleb_task.retry(exc=DoesNotExist, countdown=3,
                                     max_retries=None)
    except CypherException:
        raise create_pleb_task.retry(exc=CypherException, countdown=3,
                                     max_retries=None)

    except Exception:
        logger.exception(dumps({"function": create_pleb_task.__name__,
                                "exception": "Unhandled Exception"}))
        raise create_pleb_task.retry(exc=Exception, countdown=3,
                                     max_retries=None)