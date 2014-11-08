import pytz
import time
from json import dumps
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_posts.tasks import save_post_task
from sb_comments.utils import (save_comment,
                               delete_comment_util, get_post_comments)
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
        my_comment = save_comment(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=uuid)

        self.assertEqual(my_comment.content, "test comment")

    def test_delete_comment(self):
        uuid = str(uuid1())
        task_data = {"post_uuid": uuid, "content": "test post",
                     "current_pleb": self.user.email,
                     "wall_pleb": self.user.email}
        res = save_post_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        my_comment = save_comment(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=uuid)
        comment_deleted = delete_comment_util(my_comment.sb_id)

        self.assertEqual(comment_deleted, True)

    def test_comment_from_diff_user(self):
        uuid = str(uuid1())
        task_data = {"post_uuid": uuid, "content": "test post",
                     "current_pleb": self.user.email,
                     "wall_pleb": self.user.email}
        res = save_post_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        email = "bounce@simulator.amazonses.com"
        res = create_user_util("test", "test", email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        pleb2 = Pleb.nodes.get(email=email)
        user2 = User.objects.get(email=email)
        my_comment = save_comment(content="test comment from diff user",
                                       pleb=pleb2.email,
                                       post_uuid=uuid)

        self.assertEqual(my_comment.is_owned_by.all()[0].email,
                         pleb2.email)



class TestGetPostComments(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()

    def test_get_post_comments_success(self):
        from sb_posts.neo_models import SBPost

        post = SBPost(sb_id=str(uuid1()))
        post.save()

        for num in range(0,4):
            comment = SBComment(sb_id=str(uuid1()), content=str(uuid1()))
            comment.save()
            post.owned_by.connect(self.pleb)
            comment.is_owned_by.connect(self.pleb)
            post.comments.connect(comment)

        res = get_post_comments([post])

        self.assertEqual(type(res), list)
        self.assertIn(post.sb_id, dumps(res))

