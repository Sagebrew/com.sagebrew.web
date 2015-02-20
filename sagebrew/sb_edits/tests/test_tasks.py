import time
from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util
from sb_edits.tasks import edit_question_task, edit_object_task


class TestEditObjectTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_edit_object_task_success(self):
        question = SBQuestion(question_title='test title for edit',
                              content='this is before edit',
                              sb_id=str(uuid1())).save()
        task_data = {
            'object_uuid': question.sb_id,
            'object_type': 'sb_questions.neo_models.SBQuestion',
            'current_pleb': self.pleb,
            'content': 'this is post edit content'
        }

        res = edit_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, SBQuestion)

    def test_edit_object_task_get_object_fail(self):
        question = SBQuestion(question_title='test title for edit',
                              content='this is before edit',
                              sb_id=str(uuid1())).save()
        task_data = {
            'object_uuid': question.sb_id,
            'object_type': 'SBQuestion',
            'current_pleb': self.pleb,
            'content': 'this is post edit content'
        }

        res = edit_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)

    def test_edit_object_task_edit_content_fail(self):
        question = SBQuestion(question_title='test title for edit',
                              content='this is before edit',
                              sb_id=str(uuid1())).save()
        task_data = {
            'object_uuid': question.sb_id,
            'object_type': 'SBQuestion',
            'current_pleb': self.pleb.email,
            'content': 'this is post edit content'
        }

        res = edit_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)

class TestEditQuestionTitleTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_edit_question_title_success(self):
        question = SBQuestion(question_title='test title for edit',
                              content='this is before edit',
                              sb_id=str(uuid1())).save()
        task_data = {
            'object_uuid': question.sb_id,
            'object_type': 'sb_questions.neo_models.SBQuestion',
            'current_pleb': self.pleb,
            'question_title': 'this is post edit title'
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, SBQuestion)

    def test_edit_question_title_get_object_failure(self):
        question = SBQuestion(question_title='test title for edit',
                              content='this is before edit',
                              sb_id=str(uuid1())).save()
        task_data = {
            'object_uuid': question.sb_id,
            'object_type': 'SBQuestion',
            'current_pleb': self.pleb,
            'question_title': 'this is post edit content'
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)