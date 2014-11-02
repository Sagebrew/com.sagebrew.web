import pytz
import time
from json import dumps
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_posts.utils import save_post
from sb_posts.tasks import save_post_task
from sb_comments.utils import (save_comment_post, edit_comment_util,
                               delete_comment_util,
                               create_downvote_comment_util,
                               create_upvote_comment_util, flag_comment_util,
                               get_post_comments)
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
        my_comment = save_comment_post(content="test comment",
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
        my_comment = save_comment_post(content="test comment",
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
        my_comment = save_comment_post(content="test comment from diff user",
                                       pleb=pleb2.email,
                                       post_uuid=uuid)

        self.assertEqual(my_comment.is_owned_by.all()[0].email,
                         pleb2.email)


class TestEditComment(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_edit_comment_success(self):
        comment = SBComment(sb_id=str(uuid1()), content='test_comment')
        comment.save()
        edited_time = datetime.now(pytz.utc)
        edited_comment = edit_comment_util(comment_uuid=comment.sb_id,
                                           last_edited_on=edited_time,
                                           content="edited comment")

        self.assertTrue(edited_comment)

    def test_edit_comment_failure_more_recent_edit(self):
        now = datetime.now(pytz.utc)
        comment = SBComment(sb_id=str(uuid1()), content='test_comment')
        comment.last_edited_on = datetime.now(pytz.utc)
        comment.save()

        edited_comment = edit_comment_util(comment_uuid=comment.sb_id,
                                           last_edited_on=now,
                                           content="edited comment")

        self.assertFalse(edited_comment)

    def test_edit_comment_failure_same_content(self):
        comment = SBComment(sb_id=str(uuid1()), content='test_comment')
        comment.save()

        edited_comment = edit_comment_util(comment_uuid=comment.sb_id,
                                           content="test_comment",
                                           last_edited_on=datetime.now(
                                               pytz.utc))

        self.assertFalse(edited_comment)

    def test_edit_comment_failure_same_edit_timestamp(self):
        now = datetime.now(pytz.utc)
        comment = SBComment(sb_id=str(uuid1()), content='test_comment')
        comment.last_edited_on = now
        comment.save()

        edited_comment = edit_comment_util(comment_uuid=comment.sb_id,
                                           content="fasdf",
                                           last_edited_on=now)

        self.assertFalse(edited_comment)

    def test_edit_comment_failure_to_be_deleted(self):
        comment = SBComment(sb_id=str(uuid1()), content='test_comment')
        comment.to_be_deleted = True
        comment.save()

        edited_comment = edit_comment_util(comment_uuid=comment.sb_id,
                                           content=str(uuid1()),
                                           last_edited_on=datetime.now(
                                               pytz.utc))

        self.assertFalse(edited_comment)

class TestVoteComments(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_upvote_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.sb_id)
        create_upvote_comment_util(pleb=self.user.email,
                                   comment_uuid=my_comment.sb_id)
        my_comment.refresh()

        self.assertEqual(my_comment.up_vote_number, 1)

    def test_downvote_comment(self):
        uuid = str(uuid1())
        task_data = {"post_uuid": uuid, "content": "test post",
                     "current_pleb": self.user.email,
                     "wall_pleb": self.user.email}
        res = save_post_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        my_comment = SBComment(sb_id=uuid)
        my_comment.save()
        res = create_downvote_comment_util(pleb=self.user.email,
                                           comment_uuid=uuid)
        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 1)

    def test_upvote_from_diff_user(self):
        uuid = str(uuid1())
        task_data = {"post_uuid": uuid, "content": "test post",
                     "current_pleb": self.user.email,
                     "wall_pleb": self.user.email}
        res = save_post_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=uuid)

        email = "bounce@simulator.amazonses.com"
        res = create_user_util("test", "test", email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        pleb2 = Pleb.nodes.get(email=email)
        create_upvote_comment_util(pleb=self.user.email,
                                   comment_uuid=my_comment.sb_id)
        my_comment.refresh()
        create_upvote_comment_util(pleb=pleb2.email,
                                   comment_uuid=my_comment.sb_id)
        my_comment.refresh()

        self.assertEqual(my_comment.up_vote_number, 2)

    def test_downvote_from_diff_user(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.sb_id)
        email = "bounce@simulator.amazonses.com"
        res = create_user_util("test", "test", email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        pleb2 = Pleb.nodes.get(email=email)
        create_downvote_comment_util(pleb=self.user.email,
                                     comment_uuid=my_comment.sb_id)
        my_comment.refresh()
        create_downvote_comment_util(pleb=pleb2.email,
                                     comment_uuid=my_comment.sb_id)
        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 2)

class TestFlagComment(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_flag_comment_success_spam(self):
        comment = SBComment(sb_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.sb_id,
                                current_user=self.user.email,
                                flag_reason='spam')

        self.assertTrue(res)

    def test_flag_comment_success_explicit(self):
        comment = SBComment(sb_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.sb_id,
                                current_user=self.user.email,
                                flag_reason='explicit')

        self.assertTrue(res)

    def test_flag_comment_success_other(self):
        comment = SBComment(sb_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.sb_id,
                                current_user=self.user.email,
                                flag_reason='other')

        self.assertTrue(res)

    def test_flag_comment_failure_incorrect_reason(self):
        comment = SBComment(sb_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.sb_id,
                                current_user=self.user.email,
                                flag_reason='dumb')

        self.assertFalse(res)

    def test_flag_comment_failure_comment_does_not_exist(self):
        res = flag_comment_util(comment_uuid=uuid1(),
                                current_user=self.user.email,
                                flag_reason='other')

        self.assertEqual(res, None)

    def test_flag_comment_failure_user_does_not_exist(self):
        comment = SBComment(sb_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.sb_id,
                                current_user=uuid1(),
                                flag_reason='other')

        self.assertFalse(res)

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

