from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_registration.utils import create_user_util

from sb_edits.views import edit_question_title_view, edit_object_view


class TestEditObjectView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_edit_view_success(self):
        test_data = {'content': 'test contentasdfas', 'current_pleb': self.email,
                     'object_type': '01bb301a-644f-11e4-9ad9-080027242395',
                     'object_uuid': str(uuid1())}
        request = self.factory.post('/edit/edit_object_content_api/',
                                    data=test_data,
                                    format='json')
        request.user = self.user
        res = edit_object_view(request)

        self.assertEqual(res.status_code, 200)

    def test_edit_view_invalid_form(self):
        test_data = {'current_pleb': self.email,
                     'object_type': '01bb301a-644f-11e4-9ad9-080027242395',
                     'object_uuid': str(uuid1())}
        request = self.factory.post('/edit/edit_object_content_api/',
                                    data=test_data,
                                    format='json')
        request.user = self.user
        res = edit_object_view(request)

        self.assertEqual(res.status_code, 400)

    def test_edit_view_pleb_does_not_exist(self):
        test_data = {'content': 'test contentasdfas',
                     'current_pleb': 'fakeemail@fake.com',
                     'object_type': '01bb301a-644f-11e4-9ad9-080027242395',
                     'object_uuid': str(uuid1())}
        request = self.factory.post('/edit/edit_object_content_api/',
                                    data=test_data,
                                    format='json')
        request.user = self.user
        res = edit_object_view(request)

        self.assertEqual(res.status_code, 401)

    def test_edit_view_invalid_data_type(self):
        test_data = 123123123
        request = self.factory.post('/edit/edit_object_content_api/',
                                    data=test_data,
                                    format='json')
        request.user = self.user
        res = edit_object_view(request)

        self.assertEqual(res.status_code, 400)

class TestEditQuestionTitleView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_edit_question_title_success(self):
        data = {
            'question_title': 'testquestiontitleedit',
            'current_pleb': self.email,
            'object_type': '0274a216-644f-11e4-9ad9-080027242395',
            'object_uuid': str(uuid1())
        }
        request = self.factory.post('/edit/edit_question_title_api/',
                                    data=data,
                                    format='json')
        request.user = self.user
        res = edit_question_title_view(request)

        self.assertEqual(res.status_code, 200)

    def test_edit_question_title_invalid_form(self):
        data = {
            'contsdafent': 'testquestiontitleedit',
            'current_pleb': self.email,
            'object_type': '0274a216-644f-11e4-9ad9-080027242395',
            'object_uuid': str(uuid1())
        }
        request = self.factory.post('/edit/edit_question_title_api/',
                                    data=data,
                                    format='json')
        request.user = self.user
        res = edit_question_title_view(request)

        self.assertEqual(res.status_code, 400)

    def test_edit_question_title_pleb_does_not_exist(self):
        data = {
            'question_title': 'testquestiontitleedit',
            'current_pleb': 'fakeemail@fake.com',
            'object_type': '0274a216-644f-11e4-9ad9-080027242395',
            'object_uuid': str(uuid1())
        }
        request = self.factory.post('/edit/edit_question_title_api/',
                                    data=data,
                                    format='json')
        request.user = self.user
        res = edit_question_title_view(request)

        self.assertEqual(res.status_code, 401)

    def test_edit_question_title_invalid_data_type(self):
        data = 1231243151
        request = self.factory.post('/edit/edit_question_title_api/',
                                    data=data,
                                    format='json')
        request.user = self.user
        res = edit_question_title_view(request)

        self.assertEqual(res.status_code, 400)