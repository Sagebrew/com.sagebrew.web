from uuid import uuid1

from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.cache import cache

from neomodel import db

from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_quests.neo_models import Quest
from sagebrew.plebs.neo_models import Pleb
from sagebrew.sb_updates.neo_models import Update

from sagebrew.sb_missions.neo_models import Mission
from sagebrew.sb_missions.utils import setup_onboarding


class MissionViewTests(TestCase):

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
        self.mission = Mission(owner_username=self.user.username,
                               title=str(uuid1())).save()
        self.quest = Quest(owner_username=self.pleb.username).save()
        self.quest.missions.connect(self.mission)
        self.quest.owner.connect(self.pleb)

    def test_mission_list(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_mission_selector(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('select_mission')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_public_office(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('public_office')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_advocate_mission(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('advocate')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_account_setup(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('account_setup')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_account_setup_not_logged_in(self):
        url = reverse('account_setup')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_account_setup_no_quest(self):
        db.cypher_query('MATCH (a) OPTIONAL MATCH (a)-[r]-() DELETE a, r')
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('account_setup')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_mission_redirect(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_redirect',
                      kwargs={'object_uuid': self.mission.object_uuid})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_mission_redirect_dne(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_redirect',
                      kwargs={'object_uuid': str(uuid1())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_mission(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_mission_dne(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission',
                      kwargs={'object_uuid': str(uuid1()),
                              'slug': str(uuid1())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_mission_updates(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_updates',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        update = Update(title=str(uuid1())).save()
        update.mission.connect(self.mission)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_mission_updates_dne(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_updates',
                      kwargs={'object_uuid': str(uuid1()),
                              'slug': str(uuid1())})
        update = Update(title=str(uuid1())).save()
        update.mission.connect(self.mission)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_mission_updates_no_updates(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_updates',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_mission_updates_no_quest(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_updates',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        update = Update(title=str(uuid1())).save()
        update.mission.connect(self.mission)
        self.quest.missions.disconnect(self.mission)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_mission_settings_redirect(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_settings_redirect')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_mission_settings(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_settings',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_mission_settings_completed_wallpaper(self):
        self.quest.wallpaper_pic = "helloworld.png"
        self.quest.save()
        setup_onboarding(self.quest, self.mission)
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_settings',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_mission_settings_completed_verification(self):
        self.quest.account_verified = "verified"
        self.quest.save()
        setup_onboarding(self.quest, self.mission)
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_settings',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_mission_settings_completed_about(self):
        self.quest.about = "some short summary"
        self.quest.save()
        setup_onboarding(self.quest, self.mission)
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_settings',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_endorse(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_endorse',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_endorse_unauthorized(self):
        url = reverse('mission_endorse',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_endorsements(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_endorsements',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_endorsements_unauthorized(self):
        url = reverse('mission_endorsements',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_conversations(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_conversations',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'slug': self.mission.get_mission_title()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_conversations_does_not_exist(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('mission_conversations',
                      kwargs={'object_uuid': str(uuid1()),
                              'slug': str(uuid1())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
