import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_tag.tasks import add_auto_tags, add_tags
from sb_registration.utils import create_user_util

class TestTagTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_tag_success(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        task_dict = {'object_uuid': question.question_id,
                     'object_type': 'question',
                     'tags': tags}
        res = add_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_add_tag_failure_object_does_not_exist(self):
        question = SBQuestion(question_id=uuid1())
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
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_auto_tag_success(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        task_dict = {'tag_list': [{'object_type': 'question',
                      'object_uuid': question.question_id,
                      'tags': {'relevance': '.9', 'text': 'test'}}]}
        res = add_auto_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_add_auto_tag_wrong_object_type(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        task_dict = {'tag_list': [{'object_type': 'nothing',
                      'object_uuid': question.question_id,
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
        self.assertEqual(type(res), Exception)
