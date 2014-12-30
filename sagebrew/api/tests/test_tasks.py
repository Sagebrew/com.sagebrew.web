import time
import pytz
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util
from api.tasks import get_pleb_task, add_object_to_search_index


class TestGetPlebTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_get_pleb_task(self):
        task_data = {
            'email': 'success@simulator.amazonses.com',
            'task_func': get_pleb_task,
            'task_param': {}
        }
        res = get_pleb_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_get_pleb_task_pleb_does_not_exist(self):
        task_data = {
            'email': '11341@amazonses.com',
            'task_func': get_pleb_task,
            'task_param': {}
        }
        res = get_pleb_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)


class TestAddObjectToSearchIndex(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertFalse(isinstance(res, Exception))
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = SBQuestion(sb_id=str(uuid1()))
        self.question.save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_object_to_search_index(self):
        task_data = {
            'object_type': 'sb_questions.neo_models.SBQuestion',
            'object_data': {'content': 'fake',
                            'object_uuid': self.question.sb_id}
        }

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_add_object_to_disconnected_search_index(self):
        temp_es = settings.ELASTIC_SEARCH_HOST
        settings.ELASTIC_SEARCH_HOST = [{'host': 'sagebrew.com'}]
        task_data = {
            'object_type': 'sb_questions.neo_models.SBQuestion',
            'object_data': {'content': 'fake',
                            'object_uuid': self.question.sb_id}
        }

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        settings.ELASTIC_SEARCH_HOST = temp_es
        self.assertIsInstance(res.result, Exception)


    def test_add_object_to_search_index_pleb_already_populated(self):
        task_data = {
            'object_type': 'pleb',
            'object_data': {'email': self.email, "object_uuid": str(uuid1())},
            'object_added': self.pleb,
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
            'object_type': 'pleb',
        }

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)


