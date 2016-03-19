import time
import pytz
import requests_mock
from uuid import uuid1
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework import status

from sb_quests.neo_models import Quest
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_accounting.tasks import check_unverified_quest


class TestCheckUnverifiedQuest(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.quest = Quest(owner_username=self.pleb.username,
                           object_uuid=str(uuid1())).save()
        self.pleb.quest.connect(self.quest)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    @requests_mock.mock()
    def test_less_than_three_days(self, m):
        m.post("https://api.intercom.io/events/",
               json={
                   "event_name": "unverified-quest",
                   "user_id": self.quest.owner_username
               },
               status_code=status.HTTP_202_ACCEPTED)
        now = datetime.now(pytz.utc)
        self.quest.account_first_updated = now
        self.quest.save()
        res = check_unverified_quest.apply_async()
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    @requests_mock.mock()
    def test_greater_than_three_days(self, m):
        m.post("https://api.intercom.io/events/",
               json={
                   "event_name": "still-unverified-quest",
                   "user_id": self.quest.owner_username
               },
               status_code=status.HTTP_202_ACCEPTED)
        past = datetime.now(pytz.utc) - relativedelta(days=4)
        self.quest.account_first_updated = past
        self.quest.account_verified = "unverified"
        self.quest.save()
        res = check_unverified_quest.apply_async()
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
