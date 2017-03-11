from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIRequestFactory

from sagebrew.sb_registration.utils import create_user_util_test


class TestSearchResultView(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.save()
        cache.clear()

    def test_search_result_view_success(self):
        self.client.login(username=self.user.username, password="test_test")
        url = reverse("search_results")
        response = self.client.get(url, data={'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
