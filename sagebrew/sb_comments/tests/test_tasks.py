import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from sb_comments.neo_models import SBComment
from sb_comments.utils import save_comment_post
from sb_comments.tasks import (edit_comment_task, create_vote_comment,
                               submit_comment_on_post, flag_comment_task)
from sb_posts.utils import save_post
from sb_posts.tasks import save_post_task
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

class TestSaveComment(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
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
        response = submit_comment_on_post.apply_async(kwargs=task_param)
        while not response.ready():
            time.sleep(1)
        response = response.result
        self.assertTrue(response)


class TestEditComment(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_edit_comment_success(self):
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
        my_comment = save_comment_post(**task_param)
        edit_task_param = {'comment_uuid': my_comment.comment_id,
                           'content': 'test edit',
                           'last_edited_on': datetime.now(pytz.utc),
                           'pleb': self.user.email}
        response = edit_comment_task.apply_async(kwargs=edit_task_param)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)


class TestVoteComment(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertIsNotNone(res)
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break
        settings.CELERY_ALWAYS_EAGER = True


    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_upvote_comment(self):
        my_comment = SBComment(comment_id=str(uuid1()))
        my_comment.save()
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'up'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response.ready():
            time.sleep(1)
        response = response.result

        my_comment.refresh()

        self.assertEqual(my_comment.up_vote_number, 1)
        self.assertTrue(response)

    def test_downvote_comment(self):
        my_comment = SBComment(comment_id=str(uuid1()))
        my_comment.save()
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'down'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response.ready():
            time.sleep(1)
        response = response.result

        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 1)
        self.assertTrue(response)

    def test_upvote_comment_twice(self):
        my_comment = SBComment(comment_id=str(uuid1()))
        my_comment.save()
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'up'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response.ready():
            time.sleep(1)
        response = response.result

        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response2.ready():
            time.sleep(1)
        response2 = response2.result

        my_comment.refresh()

        self.assertEqual(my_comment.up_vote_number, 1)
        self.assertTrue(response)
        self.assertFalse(response2)

    def test_downvote_comment_twice(self):
        my_comment = SBComment(comment_id=str(uuid1()))
        my_comment.save()
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'down'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response.ready():
            time.sleep(1)
        response = response.result

        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response2.ready():
            time.sleep(1)
        response2 = response2.result

        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 1)
        self.assertTrue(response)
        self.assertFalse(response2)

    def test_upvote_then_downvote_comment(self):
        my_comment = SBComment(comment_id=str(uuid1()))
        my_comment.save()
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'up'}

        response = create_vote_comment.apply_async(kwargs=vote_task_param)

        while not response.ready():
            time.sleep(1)
        response = response.result

        vote_task_param['vote_type'] = 'down'
        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)

        while not response2.ready():
            time.sleep(1)
        response2 = response2.result

        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 0)
        self.assertEqual(my_comment.up_vote_number, 1)
        self.assertTrue(response)
        self.assertFalse(response2)

    def test_downvote_then_upvote_comment(self):
        my_comment = SBComment(comment_id=str(uuid1()))
        my_comment.save()
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'down'}

        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response.ready():
            time.sleep(1)
        response = response.result

        vote_task_param['vote_type'] = 'up'
        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response2.ready():
            time.sleep(1)
        response2 = response2.result

        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 1)
        self.assertEqual(my_comment.up_vote_number, 0)
        self.assertTrue(response)
        self.assertFalse(response2)

    def test_upvote_from_other_user(self):
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
        my_comment = save_comment_post(**task_param)
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'up'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response.ready():
            time.sleep(3)
        email = "bounce@simulator.amazonses.com"
        res = create_user_util("test", "test", email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                pleb2 = Pleb.nodes.get(email=email)
                self.user2 = User.objects.get(email=email)
            except Exception:
                pass
            else:
                break
        vote_task_param['pleb'] = pleb2.email
        vote_task_param['vote_type'] = 'up'
        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        while not response2.ready():
            time.sleep(3)

        my_comment.refresh()
        self.assertEqual(my_comment.up_vote_number, 2)
        self.assertTrue(response.result)
        self.assertTrue(response2.result)

class TestFlagCommentTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_flag_comment_success_spam(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': self.user.email,
            'flag_reason': 'spam'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_flag_comment_success_explicit(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': self.user.email,
            'flag_reason': 'explicit'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_flag_comment_success_other(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': self.user.email,
            'flag_reason': 'other'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_flag_comment_failure_incorrect_reason(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': self.user.email,
            'flag_reason': 'dumb'
        }
        response = flag_comment_task.apply_async(kwargs=task_data)
        while not response.ready():
            time.sleep(3)
        self.assertFalse(response.result)

    def test_flag_comment_failure_comment_does_not_exist(self):
        task_data = {
            'comment_uuid': uuid1(),
            'current_user': self.user.email,
            'flag_reason': 'other'
        }
        response = flag_comment_task.apply_async(kwargs=task_data)
        while not response.ready():
            time.sleep(3)
        self.assertFalse(response.result)

    def test_flag_comment_failure_user_does_not_exist(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': uuid1(),
            'flag_reason': 'other'
        }
        response = flag_comment_task.apply_async(kwargs=task_data)
        while not response.ready():
            time.sleep(3)
        self.assertFalse(response.result)