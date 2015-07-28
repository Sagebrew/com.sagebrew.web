from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from api.utils import wait_util


class ProfilePageTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()

    def test_council_page_unauthorized(self):
        url = reverse("council_page")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_council_page_authorized(self):
        self.user.username = "tyler_wiersing"
        self.user.save()
        url = reverse("council_page")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
