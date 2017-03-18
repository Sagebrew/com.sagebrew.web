from uuid import uuid1

from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.utils.text import slugify
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.cache import cache

from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_quests.neo_models import Quest
from sagebrew.sb_missions.neo_models import Mission


class ContributionViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "test_test"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)
        self.user2 = User.objects.get(email=self.email2)
        self.pleb.email_verified = True
        self.pleb.save()
        cache.clear()
        self.mission = Mission(owner_username=self.user.username,
                               title=str(uuid1())).save()
        self.quest = Quest(owner_username=self.pleb.username).save()
        self.quest2 = Quest(owner_username=self.pleb2.username).save()
        self.quest.missions.connect(self.mission)
        self.quest.owner.connect(self.pleb)

    def test_contribution_mission_get(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_donation_amount',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug':
                                  slugify(self.mission.get_mission_title())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_contribution_mission_get_dne(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_donation_amount',
                      kwargs={'object_uuid': str(uuid1()),
                              'slug': "what_what"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_contribution_quest_get(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('volunteer_choose',
                      kwargs={'username': self.quest.owner_username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_contribution_quest_get_dne(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('volunteer_choose',
                      kwargs={'username': "hello_world"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_contribution_quest_no_mission(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('volunteer_choose',
                      kwargs={'username': self.quest2.owner_username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_volunteer_option_not_authenticated(self):
        url = reverse('mission_volunteer_option',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug':
                                  slugify(self.mission.get_mission_title())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_volunteer_signup_authenticated(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_volunteer_name',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug':
                                  slugify(self.mission.get_mission_title())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_donate_signup_authenticated(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_donation_name',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug':
                                  slugify(self.mission.get_mission_title())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_donate_payment_unauthenticated(self):
        url = reverse('mission_donation_payment',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug':
                                  slugify(self.mission.get_mission_title())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
