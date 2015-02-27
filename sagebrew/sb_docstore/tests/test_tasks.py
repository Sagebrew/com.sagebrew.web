import time
from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util_test
from sb_docstore.tasks import (build_wall_task, build_question_page_task)

class TestBuildWallTask(TestCase):
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

    def test_build_wall_task(self):
        data = {'username': self.pleb.username}
        res = build_wall_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

class TestBuildQuestionPageTask(TestCase):
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

    def test_build_question_page_task(self):
        question = SBQuestion(sb_id=str(uuid1()), content='as;dlkfja;s').save()
        question.owned_by.connect(self.pleb)

        data = {'question_uuid': question.sb_id,
                'question_table': 'public_questions',
                'solution_table': 'public_solutions'}
        res = build_question_page_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)