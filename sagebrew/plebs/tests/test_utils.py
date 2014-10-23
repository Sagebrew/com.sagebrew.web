import shortuuid
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from plebs.neo_models import Pleb
from plebs.utils import prepare_user_search_html
from sb_registration.utils import create_user_util

class TestPrepareUserSearchHTML(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.username = shortuuid.uuid()
        self.password = "testpassword"
        res = create_user_util("test", "test", self.email, self.password,
                               self.username)
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_prepare_user_search_html_success(self):
        res = prepare_user_search_html(self.user.email)

        self.assertIn('<div style="font-weight: bold">Reputation: 0 | '
                      'Mutual Friends: 0</div>', res)