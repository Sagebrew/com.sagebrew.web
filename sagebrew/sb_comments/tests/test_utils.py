import time
from json import dumps
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_posts.tasks import save_post_task
from sb_comments.utils import (save_comment)
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class TestSaveComments(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_save_comment(self):
        uuid = str(uuid1())
        task_data = {"post_uuid": uuid, "content": "test post",
                     "current_pleb": self.user.email,
                     "wall_pleb": self.user.email}
        res = save_post_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        my_comment = save_comment(content="test comment")

        self.assertEqual(my_comment.content, "test comment")


