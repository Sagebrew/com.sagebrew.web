from uuid import uuid1

from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.cache import cache

from sb_registration.utils import create_user_util_test
from sb_quests.neo_models import Quest
from plebs.neo_models import Pleb
from sb_updates.neo_models import Update

from sb_missions.neo_models import Mission


class MissionViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "test_test"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()
        cache.clear()
        self.mission = Mission(owner_username=self.user.username,
                               title=str(uuid1())).save()
        self.quest = Quest(owner_username=self.pleb.username).save()
        self.quest.missions.connect(self.mission)
        self.pleb.quest.connect(self.quest)

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
        url = reverse('public_office_mission')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_advocate_mission(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('advocate')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

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
