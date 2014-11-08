import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_answers.tasks import save_answer_task
from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class TestSaveAnswerTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',}
        self.answer_info_dict = {'current_pleb': self.user.email,
                                 'content': 'test answer',
                                 'to_pleb': self.user.email}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False


    def test_save_answer_task(self):
        self.question_info_dict['sb_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        self.answer_info_dict['question_uuid'] = question.sb_id
        save_response = save_answer_task.apply_async(
            kwargs=self.answer_info_dict)

        while not save_response.ready():
            time.sleep(1)
        save_response = save_response.result

        self.assertIsNotNone(question)
        self.assertTrue(save_response)

    def test_save_answer_task_fail_due_to_question_not_existing(self):
        question_uuid = str(uuid1())
        self.answer_info_dict["question_uuid"] = question_uuid
        save_response = save_answer_task.apply_async(
            kwargs=self.answer_info_dict)

        while not save_response.ready():
            time.sleep(1)
        save_response = save_response.result
        self.assertIsInstance(save_response, Exception)


