import stripe
import time
from uuid import uuid1

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase

from neomodel import db

from sagebrew.sb_address.neo_models import Address
from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_locations.neo_models import Location
from sagebrew.sb_missions.neo_models import Mission
from sagebrew.sb_quests.neo_models import Quest

from sagebrew.sb_missions.tasks import send_reengage_message


class TestReengageTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        cache.clear()
        self.unit_under_test_name = 'quest'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        self.usa = Location(name="United States of America").save()
        self.michigan = Location(name="Michigan").save()
        self.d11 = Location(name="11", sector="federal").save()
        self.usa.encompasses.connect(self.michigan)
        self.michigan.encompassed_by.connect(self.usa)
        self.michigan.encompasses.connect(self.d11)
        self.d11.encompassed_by.connect(self.michigan)
        self.address = Address(
            street="125 Glenwood Drive",
            city="Walled Lake", state="Michigan",
            postal_code="48390",
            country="USA", county="Oakland",
            congressional_district=11, validated=True).save()
        self.address.encompassed_by.connect(self.d11)
        self.quest.address.connect(self.address)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        self.mission = Mission(owner_username=self.pleb.username,
                               title=str(uuid1()),
                               focus_name="advocacy",
                               location_name="11").save()
        self.mission.location.connect(self.d11)
        self.quest.missions.connect(self.mission)
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_send_reengage_message_political(self):
        task_data = {
            "mission_uuid": self.mission.object_uuid,
            "mission_type": "position"
        }
        res = send_reengage_message.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_send_reengage_message_advocacy(self):
        task_data = {
            "mission_uuid": self.mission.object_uuid,
            "mission_type": "advocacy"
        }
        res = send_reengage_message.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_send_reengage_no_mission(self):
        task_data = {
            "mission_uuid": "invalid uuid",
            "mission_type": "advocacy"
        }
        res = send_reengage_message.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
