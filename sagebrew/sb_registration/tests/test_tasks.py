from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb

from sb_registration.utils import create_user_util_test


class TestUpdateInterestsTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        try:
            pleb = Pleb.nodes.get(
                email='suppressionlist@simulator.amazonses.com')
            pleb.delete()
            user = User.objects.get(
                email='suppressionlist@simulator.amazonses.com')
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            self.fake_user = User.objects.create_user(
                first_name='test', last_name='test',
                email='suppressionlist@simulator.amazonses.com',
                password='fakepass',
                username='thisisafakeusername')
            self.fake_user.save()

    def tearDown(self):
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False
