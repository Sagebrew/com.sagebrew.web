from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

class TestCreateFriendRequestUtil(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    