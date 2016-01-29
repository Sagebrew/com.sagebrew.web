import time
from uuid import uuid1

from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.cache import cache

from sb_registration.utils import create_user_util_test
from plebs.neo_models import Pleb
from sb_missions.neo_models import Mission

from sb_quests.neo_models import Quest


class QuestViewTests(TestCase):
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

    def test_quest(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest', kwargs={'username': self.user.username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

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
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_quest_about_is_not_none(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest', kwargs={'username': self.user.username})
        self.quest.about = "Some Test Stuff!"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_quest_settings(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest_manage_settings',
                      kwargs={'username': self.user.username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_settings_no_quest(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('quest_manage_settings',
                      kwargs={'username': self.user.username})
        for quest in self.pleb.quest.all():
            quest.delete()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
