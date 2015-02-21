import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_comments.tasks import (save_comment_on_object,
                               create_comment_relations)
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import SBQuestion
from sb_comments.neo_models import SBComment


class TestSaveCommentTask(TestCase):
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

    def test_save_comment_on_object_task_success(self):
        question = SBQuestion(sb_id=str(uuid1())).save()
        task_param = {'content': 'test comment',
                      'current_pleb': self.pleb,
                      'object_uuid': question.sb_id,
                      'object_type': 'sb_questions.neo_models.SBQuestion',
                      'comment_uuid': str(uuid1())}
        response = save_comment_on_object.apply_async(kwargs=task_param)
        while not response.ready():
            time.sleep(1)

        self.assertTrue(response.result)

    def test_save_comment_on_object_task_get_object_fail(self):
        question = SBQuestion(sb_id=str(uuid1())).save()
        task_param = {'content': 'test comment',
                      'current_pleb': self.pleb,
                      'object_uuid': question.sb_id,
                      'object_type': 'SBQuestion',
                      'comment_uuid': str(uuid1())}
        response = save_comment_on_object.apply_async(kwargs=task_param)
        while not response.ready():
            time.sleep(1)

        self.assertFalse(response.result)

class TestCreateCommentRelationsTask(TestCase):
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

    def test_create_comment_relations_task_success(self):
        question = SBQuestion(sb_id=str(uuid1())).save()
        comment = SBComment(sb_id=str(uuid1())).save()
        task_data = {
            'current_pleb': self.pleb,
            'comment': comment,
            'sb_object': question
        }

        res = create_comment_relations.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

