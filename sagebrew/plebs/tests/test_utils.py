from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from plebs.utils import prepare_user_search_html


class TestPrepareUserSearchHTML(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Tyler",
                                             email=str(uuid1())+"@gmail.com")

    def tearDown(self):
        call_command('clear_neo_db')

    def test_prepare_user_search_html_success(self):
        res = prepare_user_search_html(self.user.email)

        self.assertIn('<div style="font-weight: bold">Reputation: 0 | '
                      'Mutual Friends: 0</div>', res)