import pytz
from uuid import uuid1
from datetime import datetime
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase

from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_registration.utils import create_user_util
from sb_docstore.utils import add_object_to_table

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
        timestamp = unicode(datetime.now(pytz.utc))
        uuid = str(uuid1())
        data = {'parent_object': uuid, 'datetime': timestamp,
                'content': "12312312312312312",}
        res = add_object_to_table('posts', data)
        self.assertTrue(res)
        test_data = {'content': 'test contentasdfas',
                     'object_type': '01bb301a-644f-11e4-9ad9-080027242395',
                     'object_uuid': uuid, 'datetime': timestamp,
                     'parent_object': uuid}
        request = self.factory.post('/edit/edit_object_content_api/',
                                    data=test_data,
                                    format='json')
        request.user = self.user
        res = edit_object_view(request)

        self.assertEqual(res.status_code, 200)

    def test_edit_view_invalid_form(self):
        test_data = {'object_type': '01bb301a-644f-11e4-9ad9-080027242395',
                     'object_uuid': str(uuid1())}
        request = self.factory.post('/edit/edit_object_content_api/',
                                    data=test_data,
                                    format='json')
        request.user = self.user
        res = edit_object_view(request)

        self.assertEqual(res.status_code, 400)

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

    def test_edit_question_title_invalid_data_type(self):
        data = 1231243151
        request = self.factory.post('/edit/edit_question_title_api/',
                                    data=data,
                                    format='json')
        request.user = self.user
        res = edit_question_title_view(request)

        self.assertEqual(res.status_code, 400)