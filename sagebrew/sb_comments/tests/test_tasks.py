import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_comments.tasks import (save_comment_on_object)
from sb_posts.tasks import save_post_task
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class TestSaveComment(TestCase):
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

    def test_save_comment_on_post_task(self):
        uuid = str(uuid1())
        task_data = {"post_uuid": uuid, "content": "test post",
                     "current_pleb": self.user.email,
                     "wall_pleb": self.user.email}
        res = save_post_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': uuid}
        response = save_comment_on_object.apply_async(kwargs=task_param)
        while not response.ready():
            time.sleep(1)
        response = response.result
        self.assertTrue(response)

