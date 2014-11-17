from django.test import TestCase, Client
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class HelpGoodQuestionTests(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_save_post_view_correct_data(self):
        response = self.client.get('/help/good_question/')
        # TODO is it possible to check if spelling is correct
        # in response.content?
        self.assertEqual(response.status_code, 200)