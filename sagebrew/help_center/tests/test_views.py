from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test


class HelpGoodQuestionTests(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_good_question_helper(self):
        response = self.client.get(reverse('good_question'), follow=True)
        self.assertEqual(response.status_code, 200)
