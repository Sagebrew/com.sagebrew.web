from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from api.utils import test_wait_util
from sb_registration.utils import create_user_util

from sb_edits.views import edit_question_title_view, edit_object_view


class TestEditQuestionView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_edit_question_view_success(self):
        test_data = {'content': 'test contentasdfas', 'current_pleb': self.email,
                     'object_type': '01bb301a-644f-11e4-9ad9-080027242395',
                     'object_uuid': str(uuid1())}
        request = self.factory.post('/edit/edit_object_content_api/',
                                    data=test_data,
                                    format='json')
        request.user = self.user
        res = edit_object_view(request)

        self.assertEqual(res.status_code, 200)
