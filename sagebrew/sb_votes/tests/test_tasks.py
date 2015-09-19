import time
from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb

from sb_base.neo_models import VotableContent
from sb_registration.utils import create_user_util_test
from sb_votes.tasks import vote_object_task, object_vote_notifications

from sb_questions.neo_models import Question


class TestVoteObjectTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_vote_object_task_success(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1())).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'object_uuid': question.object_uuid,
            'current_pleb': self.pleb.username,
            'vote_type': True
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, VotableContent)


class TestObjectVoteNotifications(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        self.question = Question(owner_username=self.pleb.username).save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_initial_vote_create(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": None,
            "new_vote_type": 1,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_change_vote_down_to_up(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 0,
            "new_vote_type": 1,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_change_vote_up_to_down(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 1,
            "new_vote_type": 0,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_pos_rep_change(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 0,
            "new_vote_type": 1,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_neg_rep_change(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 1,
            "new_vote_type": 0,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_pleb_does_not_exist(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 1,
            "new_vote_type": 0,
            "voting_pleb": str(uuid1())
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)
