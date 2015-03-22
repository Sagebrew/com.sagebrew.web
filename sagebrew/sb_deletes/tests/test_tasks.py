import time
from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util_test
from sb_deletes.tasks import delete_object_task


class TestDeleteObjectTask(TestCase):
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

    def test_delete_object_task_success(self):
        question = SBQuestion(question_title='test title for delete',
                              content='this is before delete',
                              object_uuid=str(uuid1())).save()
        task_data = {
            'object_type': 'sb_questions.neo_models.SBQuestion',
            'object_uuid': question.object_uuid,
            'current_pleb': self.pleb
        }
        res = delete_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_delete_object_task_get_object_fail(self):
        question = SBQuestion(question_title='test title for delete',
                              content='this is before delete',
                              object_uuid=str(uuid1())).save()
        task_data = {
            'object_type': 'SBQuestion',
            'object_uuid': question.object_uuid,
            'current_pleb': self.pleb
        }
        res = delete_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)

