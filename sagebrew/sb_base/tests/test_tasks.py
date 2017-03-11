from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context

from intercom import ResourceNotFound

from sagebrew.sb_base.tasks import create_event, create_email
from sagebrew.sb_registration.utils import create_user_util_test


class TestCreateEventTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_event_with_metadata(self):
        task_data = {
            'username': self.user.username,
            'event_name': 'signup-no-mission',
            'metadata': {'hello': 'world'}
        }
        res = create_event.apply_async(kwargs=task_data)
        self.assertFalse(isinstance(res.result, ResourceNotFound))

    def test_create_event_without_metadata(self):
        task_data = {
            'username': self.user.username,
            'event_name': 'signup-no-mission'
        }
        res = create_event.apply_async(kwargs=task_data)
        self.assertFalse(isinstance(res.result, ResourceNotFound))


class TestCreateMessageTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_email_with_metadata(self):
        from sagebrew.plebs.serializers import EmailAuthTokenGenerator
        message_data = {
            'message_type': 'email',
            'subject': 'Sagebrew Email Verification',
            'body': get_template('email_templates/verification.html').render(
                Context({
                    'first_name': self.user.first_name,
                    'verification_url': "%s%s%s" % (
                        settings.EMAIL_VERIFICATION_URL,
                        EmailAuthTokenGenerator()
                            .make_token(self.user, self.pleb), '/')
                })),
            'template': "personal",
            'from': {
                'type': "admin",
                'id': settings.INTERCOM_ADMIN_ID_DEVON
            },
            'to': {
                'type': "user",
                'user_id': self.user.username
            }
        }
        res = create_email.apply_async(kwargs={'message_data': message_data})
        self.assertFalse(isinstance(res.result, ResourceNotFound))
