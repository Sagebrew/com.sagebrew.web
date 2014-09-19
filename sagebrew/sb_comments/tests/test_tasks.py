import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from sb_comments.neo_models import SBComment
from sb_comments.utils import save_comment_post
from sb_comments.tasks import (edit_comment_task, create_vote_comment,
                               submit_comment_on_post, flag_comment_task)
from sb_posts.utils import save_post
from plebs.neo_models import Pleb


class TestSaveComment(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_save_comment_on_post_task(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        response = submit_comment_on_post.apply_async(kwargs=task_param)
        time.sleep(1)
        self.assertTrue(response.get())


class TestEditComment(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_edit_comment_success(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        my_comment = save_comment_post(**task_param)
        edit_task_param = {'comment_uuid': my_comment.comment_id,
                           'content': 'test edit',
                           'last_edited_on': datetime.now(pytz.utc),
                           'pleb': self.user.email}
        response = edit_comment_task.apply_async(kwargs=edit_task_param)
        time.sleep(1)
        self.assertTrue(response.get())


class TestVoteComment(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_upvote_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        my_comment = save_comment_post(**task_param)
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'up'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        response = response.get()

        my_comment.refresh()

        self.assertEqual(my_comment.up_vote_number, 1)
        self.assertTrue(response)

    def test_downvote_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        my_comment = save_comment_post(**task_param)
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'down'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        response = response.get()

        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 1)
        self.assertTrue(response)

    def test_upvote_comment_twice(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        my_comment = save_comment_post(**task_param)
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'up'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        response = response.get()

        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        response2 = response2.get()

        my_comment.refresh()

        self.assertEqual(my_comment.up_vote_number, 1)
        self.assertTrue(response)
        self.assertFalse(response2)

    def test_downvote_comment_twice(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        my_comment = save_comment_post(**task_param)
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'down'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        response = response.get()

        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        response2 = response2.get()

        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 1)
        self.assertTrue(response)
        self.assertFalse(response2)

    def test_upvote_then_downvote_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        my_comment = save_comment_post(**task_param)
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'up'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        response = response.get()
        vote_task_param['vote_type'] = 'down'
        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        response2 = response2.get()

        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 0)
        self.assertEqual(my_comment.up_vote_number, 1)
        self.assertTrue(response)
        self.assertFalse(response2)

    def test_downvote_then_upvote_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        my_comment = save_comment_post(**task_param)
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'down'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        response = response.get()
        vote_task_param['vote_type'] = 'up'
        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        response2 = response2.get()

        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 1)
        self.assertEqual(my_comment.up_vote_number, 0)
        self.assertTrue(response)
        self.assertFalse(response2)

    def test_upvote_from_other_user(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        task_param = {'content': 'test comment',
                      'pleb': self.user.email,
                      'post_uuid': post.post_id}
        my_comment = save_comment_post(**task_param)
        vote_task_param = {'pleb': self.user.email,
                           'comment_uuid': my_comment.comment_id,
                           'vote_type': 'up'}
        response = create_vote_comment.apply_async(kwargs=vote_task_param)
        response = response.get()
        user2 = User.objects.create_user(
            username='Test' + str(uuid1())[:25],
            email=str(uuid1())[:10] + "@gmail.com")
        pleb2 = Pleb.nodes.get(email=user2.email)
        vote_task_param['pleb'] = pleb2.email
        vote_task_param['vote_type'] = 'up'
        response2 = create_vote_comment.apply_async(kwargs=vote_task_param)
        response2 = response2.get()

        my_comment.refresh()
        self.assertEqual(my_comment.up_vote_number, 2)
        self.assertTrue(response)
        self.assertTrue(response2)

class TestFlagCommentTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_flag_comment_success_spam(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': self.user.email,
            'flag_reason': 'spam'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)

        self.assertTrue(res.get())

    def test_flag_comment_success_explicit(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': self.user.email,
            'flag_reason': 'explicit'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)

        self.assertTrue(res.get())

    def test_flag_comment_success_other(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': self.user.email,
            'flag_reason': 'other'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)

        self.assertTrue(res.get())

    def test_flag_comment_failure_incorrect_reason(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': self.user.email,
            'flag_reason': 'dumb'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)

        self.assertFalse(res.get())

    def test_flag_comment_failure_comment_does_not_exist(self):
        task_data = {
            'comment_uuid': uuid1(),
            'current_user': self.user.email,
            'flag_reason': 'other'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)

        self.assertFalse(res.get())

    def test_flag_comment_failure_user_does_not_exist(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        task_data = {
            'comment_uuid': comment.comment_id,
            'current_user': uuid1(),
            'flag_reason': 'other'
        }
        res = flag_comment_task.apply_async(kwargs=task_data)

        self.assertFalse(res.get())