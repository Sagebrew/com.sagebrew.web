import time
import pytz
import logging
from datetime import datetime, timedelta
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_posts.utils import save_post, edit_post_info, delete_post_info, \
    create_post_vote, flag_post
from sb_posts.tasks import save_post_task
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

logger = logging.getLogger('loggly_logs')

class TestSavePost(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_save_post(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.pleb.email,
                         wall_pleb=self.pleb.email)

        self.assertIsNot(post, False)


    def test_post_already_exists(self):
        post_info_dict = {'current_pleb': self.pleb.email,
                          'wall_pleb': self.pleb.email,
                          'content': 'test post',
                          'post_uuid': str(uuid1())}

        prev_post = SBPost(content='test', post_id=post_info_dict['post_uuid'])
        prev_post.save()
        post = save_post(post_uuid=post_info_dict['post_uuid'],
                         content='test post',
                         current_pleb=self.pleb.email,
                         wall_pleb=self.pleb.email)
        self.assertFalse(post)

    def test_edit_post(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', post_id=uuid,
                           last_edited_on=datetime.now(pytz.utc),
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email)
        test_post.save()
        edited_post = edit_post_info(content='post edited', post_uuid=uuid,
                                     current_pleb=self.pleb.email)

        self.assertEqual(test_post.post_id, uuid)
        self.assertTrue(edited_post)

    def test_delete_post(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', post_id=uuid,
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email)
        test_post.save()
        if delete_post_info(uuid):
            try:
                post = SBPost.nodes.get(post_id=uuid)
            except SBPost.DoesNotExist:
                return

    def test_edit_post_to_be_deleted(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', post_id=uuid,
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email,
                           to_be_deleted=True)
        test_post.save()

        edited_post = edit_post_info(content='post edited',
                                     post_uuid=uuid,
                                     current_pleb=self.pleb.email)

        self.assertEqual(edited_post['detail'], 'to be deleted')

    def test_edit_post_same_content(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', post_id=uuid,
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email)
        test_post.save()

        edited_post = edit_post_info(content='test', post_uuid=uuid,
                                     current_pleb=self.pleb.email)

        self.assertEqual(edited_post['detail'], 'content is the same')

    def test_edit_post_same_timestamp(self):
        uuid = str(uuid1())
        edit_time = datetime.now(pytz.UTC)
        test_post = SBPost(content='test', post_id=uuid,
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email,
                           last_edited_on=edit_time)
        test_post.save()
        edited_post = edit_post_info(content='post edited', post_uuid=uuid,
                                     last_edited_on=edit_time,
                                     current_pleb=self.pleb.email)

        self.assertEqual(edited_post['detail'], 'time stamp is the same')

    def test_edit_post_with_earlier_time(self):
        uuid = str(uuid1())
        now = datetime.now(pytz.utc)
        future_edit = now + timedelta(minutes=10)
        test_post = SBPost(content='test', post_id=uuid,
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email,
                           last_edited_on=future_edit)
        test_post.save()

        edited_post = edit_post_info(content='post edited',
                                     post_uuid=uuid,
                                     last_edited_on=datetime.now(pytz.utc),
                                     current_pleb=self.pleb.email)

        self.assertEqual(edited_post['detail'], 'last edit more recent')


class TestPostVotes(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_upvote_post(self):
        uuid = str(uuid1())
        task_data = {"post_uuid": uuid, "content": "test post",
                     "current_pleb": self.user.email,
                     "wall_pleb": self.user.email}
        res = save_post_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = create_post_vote(pleb=self.pleb.email, post_uuid=uuid,
                         vote_type="up")
        self.assertTrue(res)


    def test_downvote_post(self):
        uuid = str(uuid1())
        task_data = {"post_uuid": uuid, "content": "test post",
                     "current_pleb": self.user.email,
                     "wall_pleb": self.user.email}
        res = save_post_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = create_post_vote(pleb=self.pleb.email, post_uuid=uuid,
                         vote_type="down")

        self.assertTrue(res)


    def test_downvote_twice(self):
        uuid = str(uuid1())
        post = SBPost(post_id=uuid, content='test')
        post.save()
        pleb = Pleb.nodes.get(email=self.pleb.email)
        post.down_voted_by.connect(pleb)
        res = create_post_vote(pleb=self.pleb.email, post_uuid=post.post_id,
                         vote_type="down")

        self.assertFalse(res)


    def test_upvote_twice(self):
        uuid = str(uuid1())
        post = SBPost(post_id=uuid, content='test')
        post.save()
        pleb = Pleb.nodes.get(email=self.pleb.email)
        post.up_voted_by.connect(pleb)
        res = create_post_vote(pleb=self.pleb.email, post_uuid=post.post_id,
                         vote_type="up")

        self.assertFalse(res)


class TestFlagPost(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_flag_success_spam(self):
        post = SBPost(post_id=uuid1())
        post.save()
        res = flag_post(post_uuid=post.post_id, current_user=self.pleb.email,
                        flag_reason='spam')

        self.assertTrue(res)

    def test_flag_success_explicit(self):
        post = SBPost(post_id=uuid1())
        post.save()
        res = flag_post(post_uuid=post.post_id, current_user=self.pleb.email,
                        flag_reason='explicit')

        self.assertTrue(res)

    def test_flag_success_other(self):
        post = SBPost(post_id=uuid1())
        post.save()
        res = flag_post(post_uuid=post.post_id, current_user=self.pleb.email,
                        flag_reason='other')

        self.assertTrue(res)

    def test_flag_failure_wrong_data_incorrect_reason(self):
        post = SBPost(post_id=uuid1())
        post.save()
        res = flag_post(post_uuid=post.post_id, current_user=self.pleb.email,
                        flag_reason='dumb')

        self.assertFalse(res)

    def test_flag_failure_post_does_not_exist(self):
        res = flag_post(post_uuid=uuid1(), current_user=self.pleb.email,
                        flag_reason='other')

        self.assertFalse(res)

    def test_flag_failure_user_does_not_exist(self):
        post = SBPost(post_id=uuid1())
        post.save()
        res = flag_post(post_uuid=post.post_id, current_user=uuid1(),
                        flag_reason='other')

        self.assertFalse(res)
