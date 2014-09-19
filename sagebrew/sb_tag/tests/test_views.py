from uuid import uuid1

from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.management import call_command

from plebs.neo_models import Pleb
from sb_tag.views import get_tag_view

class TestTagViews(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_get_tag_view_success(self):
        request = self.factory.get('/tags/get_tags/')
        request.user = self.user
        response = get_tag_view(request)

        self.assertEqual(response.status_code, 200)