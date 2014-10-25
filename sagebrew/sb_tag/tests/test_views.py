from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase

from api.utils import test_wait_util
from plebs.neo_models import Pleb
from sb_tag.views import get_tag_view
from sb_registration.utils import create_user_util

class TestTagViews(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_tag_view_success(self):
        request = self.factory.get('/tags/get_tags/')
        request.user = self.user
        response = get_tag_view(request)

        self.assertEqual(response.status_code, 200)