from uuid import uuid1
from celery import shared_task
from logging import getLogger
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from neomodel import DoesNotExist

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from sb_search.tasks import add_user_to_custom_index
from sb_wall.neo_models import SBWall
from sb_registration.models import EmailAuthTokenGenerator
from sb_registration.utils import sb_send_email

logger = getLogger('loggly_logs')
token_gen = EmailAuthTokenGenerator()

@shared_task()
def send_email_task(to, subject, text_content, html_content):
    try:
        sb_send_email(to, subject, text_content, html_content)
    except Exception:
        logger.exception({"function": send_email_task.__name__,
                          "exception": "UnhandledException: "})
        raise send_email_task.retry(exc=Exception, countdown=3,
                                    max_retries=None)

@shared_task()
def create_pleb_task(user_instance):
    from plebs.neo_models import Pleb
    try:
        try:
            test = Pleb.nodes.get(email=user_instance.email)
            return False
        except (Pleb.DoesNotExist, DoesNotExist):
            pleb = Pleb(email=user_instance.email,
                        first_name=user_instance.first_name,
                        last_name=user_instance.last_name)
            pleb.save()
            wall = SBWall(wall_id=uuid1())
            wall.save()
            wall.owner.connect(pleb)
            pleb.wall.connect(pleb)
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
            template_dict = {
                'full_name': pleb.first_name+' '+pleb.last_name,
                'verification_url': settings.EMAIL_VERIFICATION_URL+
                                    token_gen.make_token(user_instance)+'/'
            }
            subject, to = "Sagebrew Email Verification", pleb.email
            text_content = get_template(
                'email_templates/email_verification.txt').\
                render(Context(template_dict))
            html_content = get_template(
                'email_templates/email_verification.html').\
                render(Context(template_dict))
            sb_send_email(to, subject, text_content, html_content)
            return True
    except Exception:
        logger.exception({"function": create_pleb_task.__name__,
                          "exception": "UnhandledException: "})
        raise create_pleb_task.retry(exc=Exception, countdown=3,
                                     max_retries=None)

