from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase

from plebs.neo_models import Pleb
from sb_tag.views import get_tag_view

class TestTagViews(TestCase):
    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@gmail.com')
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')

    def test_get_tag_view_success(self):
        request = self.factory.get('/tags/get_tags/')
        request.user = self.user
        response = get_tag_view(request)

        self.assertEqual(response.status_code, 200)