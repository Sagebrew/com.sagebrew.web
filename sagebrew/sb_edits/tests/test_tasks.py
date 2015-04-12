import time
from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test
from sb_edits.tasks import edit_question_task, edit_object_task


class TestEditObjectTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_edit_object_task_success(self):
        question = Question(title='test title for edit',
                              content='this is before edit',
                              object_uuid=str(uuid1())).save()
        task_data = {
            'object_uuid': question.object_uuid,
            'object_type': 'sb_questions.neo_models.Question',
            'username': self.pleb.username,
            'content': 'this is post edit content'
        }

        res = edit_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Question)

    def test_edit_object_task_get_object_fail(self):
        question = Question(title='test title for edit',
                              content='this is before edit',
                              object_uuid=str(uuid1())).save()
        task_data = {
            'object_uuid': question.object_uuid,
            'object_type': 'Question',
            'username': self.pleb.username,
            'content': 'this is post edit content'
        }

        res = edit_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)

    def test_edit_object_task_edit_content_fail(self):
        question = Question(title='test title for edit',
                              content='this is before edit',
                              object_uuid=str(uuid1())).save()
        task_data = {
            'object_uuid': question.object_uuid,
            'object_type': 'Question',
            'username': self.pleb.username,
            'content': 'this is post edit content'
        }

        res = edit_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)

class TestEditQuestionTitleTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_edit_title_success(self):
        question = Question(title='test title for edit',
                              content='this is before edit',
                              object_uuid=str(uuid1())).save()
        task_data = {
            'object_uuid': question.object_uuid,
            'object_type': 'sb_questions.neo_models.Question',
            'title': 'this is post edit title'
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Question)

    def test_edit_title_get_object_failure(self):
        question = Question(title='test title for edit',
                              content='this is before edit',
                              object_uuid=str(uuid1())).save()
        task_data = {
            'object_uuid': question.object_uuid,
            'object_type': 'Question',
            'title': 'this is post edit content'
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)