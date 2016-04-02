from uuid import uuid1

from rest_framework import status
from rest_framework.reverse import reverse

from django.utils.text import slugify
from django.core.cache import cache
from django.contrib.auth.models import User
from django.test import TestCase, Client

from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission
from sb_registration.utils import create_user_util_test
from sb_updates.neo_models import Update


class TestMissionUpdateView(TestCase):

    def setUp(self):
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "test_test"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()
        self.update = Update().save()
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        cache.clear()
        self.mission = Mission(owner_username=self.pleb.username,
                               title=str(uuid1()),
                               focus_name="advocacy").save()
        self.quest.missions.connect(self.mission)
        self.update.mission.connect(self.mission)
        cache.set(self.pleb.username, self.pleb)

    def test_edit_update(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse("mission_edit_update",
                      kwargs={"object_uuid": self.mission.object_uuid,
                              "edit_id": self.update.object_uuid,
                              "slug": slugify(
                                  self.mission.get_mission_title())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_edit_update_doesnt_exist(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse("mission_edit_update",
                      kwargs={"object_uuid": self.mission.object_uuid,
                              "edit_id": self.update.object_uuid,
                              "slug": slugify(
                                  self.mission.get_mission_title())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
