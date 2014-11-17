import time
from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util
from sb_votes.tasks import vote_object_task


class TestVoteObjectTask(TestCase):
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

    def test_vote_object_task_success(self):
        question = SBQuestion(sb_id=str(uuid1())).save()
        task_data = {
            'object_type': 'sb_questions.neo_models.SBQuestion',
            'object_uuid': question.sb_id,
            'current_pleb': self.pleb,
            'vote_type': True
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, SBQuestion)

    def test_vote_object_task_get_object_failure(self):
        question = SBQuestion(sb_id=str(uuid1())).save()
        task_data = {
            'object_type': 'SBQuestion',
            'object_uuid': question.sb_id,
            'current_pleb': self.pleb,
            'vote_type': True
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)

    def test_vote_object_task_vote_method_failure(self):
        question = SBQuestion(sb_id=str(uuid1())).save()
        task_data = {
            'object_type': 'sb_questions.neo_models.SBQuestion',
            'object_uuid': question.sb_id,
            'current_pleb': self.email,
            'vote_type': True
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)