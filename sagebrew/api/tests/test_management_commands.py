import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User

from plebs.neo_models import Pleb


class TestClearNeoDBCommand(TestCase):

    def test_clear_neo_db(self):
        email = 'devon@sagebrew.com'
        user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=email)
        pleb = Pleb.nodes.get(email=email)
        self.assertEqual(pleb.email, user.email)
        call_command("clear_neo_db")
        pleb = None
        try:
            pleb = Pleb.nodes.get(email=email)
            self.assertIsNone(pleb)
        except Pleb.DoesNotExist:
            self.assertIsNone(pleb)
