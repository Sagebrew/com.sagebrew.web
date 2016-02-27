from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from sb_registration.utils import create_user_util_test
from sb_council.views import CouncilView


class ProfilePageTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()

    def test_council_page_unauthorized(self):
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = AnonymousUser()
        council_page = CouncilView.as_view()
        response = council_page(request, self.pleb.username)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_council_page_authorized(self):
        self.pleb.reputation = 10001
        self.pleb.save()
        cache.clear()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        council_page = CouncilView.as_view()
        response = council_page(request, self.pleb.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_council_page_not_admin(self):
        self.pleb.reputation = 0
        self.pleb.save()
        cache.clear()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        council_page = CouncilView.as_view()
        response = council_page(request, self.pleb.username)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
