import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_tag.tasks import add_auto_tags, add_tags
from sb_registration.utils import create_user_util

class TestTagTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_tag_success(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        task_dict = {'object_uuid': question.sb_id,
                     'object_type': 'question',
                     'tags': tags}
        res = add_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_add_tag_failure_object_does_not_exist(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        task_dict = {'object_uuid': '1',
                     'object_type': 'nothing',
                     'tags': tags}
        res = add_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertFalse(res)


class TestAutoTagTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_auto_tag_success(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        task_dict = {'tag_list': [{'object_type': 'question',
                      'object_uuid': question.sb_id,
                      'tags': {'relevance': '.9',
                               'text': 'test'}}]}
        res = add_auto_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_add_auto_tag_wrong_object_type(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        task_dict = {'tag_list': [{'object_type': 'nothing',
                      'object_uuid': question.sb_id,
                      'tags': {'relevance': '.9', 'text': 'test'}}]}
        res = add_auto_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertFalse(res)

    def test_add_auto_tag_object_does_not_exist(self):
        task_dict = {'tag_list': [{'object_type': 'question',
                      'object_uuid': str(uuid1()),
                      'tags': {'relevance': '.9', 'text': 'test'}}]}
        res = add_auto_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(isinstance(res, Exception))
