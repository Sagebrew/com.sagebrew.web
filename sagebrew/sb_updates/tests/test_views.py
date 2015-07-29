from uuid import uuid1

from rest_framework import status
from rest_framework.reverse import reverse

from django.core.cache import cache
from django.contrib.auth.models import User
from django.test import TestCase, Client

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_updates.neo_models import Update


class ProfilePageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()
        self.client.login(username=self.user.username, password=self.password)
        self.update = Update().save()
        cache.clear()

    def test_edit_update(self):
        url = reverse("update-edit",
                      kwargs={"object_uuid": self.update.object_uuid})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_edit_update_doesnt_exist(self):
        url = reverse("update-edit",
                      kwargs={"object_uuid": str(uuid1())})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
