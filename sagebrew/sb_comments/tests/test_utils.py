import pytz
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from sb_posts.utils import save_post
from sb_comments.utils import (save_comment_post, edit_comment_util,
                               delete_comment_util,
                               create_downvote_comment_util,
                               create_upvote_comment_util, flag_comment_util)
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb


class TestSaveComments(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_save_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.post_id)

        self.assertEqual(my_comment.content, "test comment")

    def test_edit_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.post_id)
        edited_time = datetime.now(pytz.utc)
        edited_comment = edit_comment_util(comment_uuid=my_comment.comment_id,
                                           last_edited_on=edited_time,
                                           content="edited comment", pleb="")

        self.assertEqual(edited_comment, True)

    def test_delete_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.post_id)
        comment_deleted = delete_comment_util(my_comment.comment_id)

        self.assertEqual(comment_deleted, True)

    def test_comment_from_diff_user(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        user2 = User.objects.create_user(
            username='Test' + str(uuid1())[:25],
            email=str(uuid1())[:10] + "@gmail.com")
        pleb2 = Pleb.nodes.get(email=user2.email)
        my_comment = save_comment_post(content="test comment from diff user",
                                       pleb=pleb2.email,
                                       post_uuid=post.post_id)

        self.assertEqual(my_comment.traverse('is_owned_by').run()[0].email,
                         pleb2.email)


class TestVoteComments(TestCase):
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
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.post_id)
        create_upvote_comment_util(pleb=self.user.email,
                                   comment_uuid=my_comment.comment_id)
        my_comment.refresh()

        self.assertEqual(my_comment.up_vote_number, 1)

    def test_downvote_comment(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.post_id)
        create_downvote_comment_util(pleb=self.user.email,
                                     comment_uuid=my_comment.comment_id)
        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 1)

    def test_upvote_from_diff_user(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.post_id)

        user2 = User.objects.create_user(
            username='Test' + str(uuid1())[:25],
            email=str(uuid1())[:10] + "@gmail.com")
        pleb2 = Pleb.nodes.get(email=user2.email)

        create_upvote_comment_util(pleb=self.user.email,
                                   comment_uuid=my_comment.comment_id)
        my_comment.refresh()
        create_upvote_comment_util(pleb=pleb2.email,
                                   comment_uuid=my_comment.comment_id)
        my_comment.refresh()

        self.assertEqual(my_comment.up_vote_number, 2)

    def test_downvote_from_diff_user(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.user.email,
                         wall_pleb=self.user.email)
        my_comment = save_comment_post(content="test comment",
                                       pleb=self.user.email,
                                       post_uuid=post.post_id)
        user2 = User.objects.create_user(
            username='Test' + str(uuid1())[:25],
            email=str(uuid1())[:10] + "@gmail.com")
        pleb2 = Pleb.nodes.get(email=user2.email)
        create_downvote_comment_util(pleb=self.user.email,
                                     comment_uuid=my_comment.comment_id)
        my_comment.refresh()
        create_downvote_comment_util(pleb=pleb2.email,
                                     comment_uuid=my_comment.comment_id)
        my_comment.refresh()

        self.assertEqual(my_comment.down_vote_number, 2)

class TestFlagComment(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_flag_comment_success_spam(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.comment_id,
                                current_user=self.user.email,
                                flag_reason='spam')

        self.assertTrue(res)

    def test_flag_comment_success_explicit(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.comment_id,
                                current_user=self.user.email,
                                flag_reason='explicit')

        self.assertTrue(res)

    def test_flag_comment_success_other(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.comment_id,
                                current_user=self.user.email,
                                flag_reason='other')

        self.assertTrue(res)

    def test_flag_comment_failure_incorrect_reason(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.comment_id,
                                current_user=self.user.email,
                                flag_reason='dumb')

        self.assertFalse(res)

    def test_flag_comment_failure_comment_does_not_exist(self):
        res = flag_comment_util(comment_uuid=uuid1(),
                                current_user=self.user.email,
                                flag_reason='other')

        self.assertFalse(res)

    def test_flag_comment_failure_user_does_not_exist(self):
        comment = SBComment(comment_id=uuid1())
        comment.save()
        res = flag_comment_util(comment_uuid=comment.comment_id,
                                current_user=uuid1(),
                                flag_reason='other')

        self.assertFalse(res)