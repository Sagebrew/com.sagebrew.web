import time
from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test
from api.tasks import add_object_to_search_index


class TestAddObjectToSearchIndex(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertFalse(isinstance(res, Exception))
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(object_uuid=str(uuid1()))
        self.question.save()
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_object_to_search_index(self):
        task_data = {
            'object_uuid': self.question.object_uuid,
            'object_data': {
                'type': 'question',
                'id': self.question.object_uuid,
                'content': 'fake',
                'object_uuid': self.question.object_uuid}
        }

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_add_object_to_disconnected_search_index(self):
        temp_es = settings.ELASTIC_SEARCH_HOST
        settings.ELASTIC_SEARCH_HOST = [{'host': 'sagebrew.com'}]
        task_data = {
            'object_uuid': self.question.object_uuid,
            'object_data': {
                'type': 'question',
                'id': self.question.object_uuid,
                'content': 'fake',
                'object_uuid': self.question.object_uuid}
        }

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        settings.ELASTIC_SEARCH_HOST = temp_es
        self.assertIsInstance(res.result, Exception)

    def test_add_object_to_search_index_pleb_already_populated(self):
        fake_uuid = str(uuid1())
        task_data = {
            'object_uuid': fake_uuid,
            'object_data': {
                'type': 'question',
                'id': self.question.object_uuid,
                'email': self.email,
                "object_uuid": fake_uuid
            },
        }
        self.pleb.populated_es_index = True
        self.pleb.save()

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.pleb.populated_es_index = False
        self.pleb.save()

    def test_add_object_to_search_index_no_object_data(self):
        task_data = {
            'object_uuid': str(uuid1()),
        }

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)
