import time
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from plebs.neo_models import Pleb
from plebs.utils import prepare_user_search_html
from sb_registration.utils import create_user_util

class TestPrepareUserSearchHTML(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')

    def test_prepare_user_search_html_success(self):
        res = prepare_user_search_html(self.user.email)

        self.assertIn('<div style="font-weight: bold">Reputation: 0 | '
                      'Mutual Friends: 0</div>', res)