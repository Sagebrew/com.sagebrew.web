from uuid import uuid1

from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.cache import cache

from neomodel import db

from sagebrew.sb_address.neo_models import Address
from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.plebs.neo_models import Pleb
from sagebrew.sb_missions.neo_models import Mission
from sagebrew.sb_missions.utils import setup_onboarding

from sagebrew.sb_quests.neo_models import Quest


class QuestViewTests(TestCase):

    def setUp(self):
        db.cypher_query('MATCH (a) OPTIONAL MATCH (a)-[r]-() DELETE a, r')
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "test_test"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()
        cache.clear()
        self.mission = Mission(
            owner_username=self.user.username, title=str(uuid1()),
            focus_on_type="advocacy", focus_name="testing advocacy",
            district=None).save()
        self.quest = Quest(owner_username=self.pleb.username).save()
        self.quest.missions.connect(self.mission)
        self.quest.owner.connect(self.pleb)
        setup_onboarding(self.quest, self.mission)

    def test_quest(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest', kwargs={'username': self.user.username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_quest_dne(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest', kwargs={'username': str(uuid1())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_quest_about_is_none(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest', kwargs={'username': self.user.username})
        self.quest.about = None
        self.quest.save()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_quest_about_is_not_none(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest', kwargs={'username': self.user.username})
        self.quest.about = "Some Test Stuff!"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_quest_settings(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest_manage_settings',
                      kwargs={'username': self.user.username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_quest_settings_with_address(self):
        address = Address(street="3295 Rio Vista St",
                          city="Commerce Township", state="MI",
                          postal_code="48382", country="US",
                          congressional_district="11").save()
        self.quest.address.connect(address)
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest_manage_settings',
                      kwargs={'username': self.user.username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_settings_no_quest(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest_manage_settings',
                      kwargs={'username': self.user.username})
        query = "MATCH (n) OPTIONAL MATCH " \
                "(n)-[r]-() DELETE n, r"
        res, _ = db.cypher_query(query)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_settings_no_mission(self):
        db.cypher_query('MATCH (a:Mission) OPTIONAL MATCH (a)-[r]-()'
                        ' DELETE a, r')
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest_manage_settings',
                      kwargs={'username': self.user.username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
