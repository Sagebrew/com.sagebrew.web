import time
import pytz
import logging
from datetime import datetime, timedelta
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_posts.utils import save_post, edit_post_info, delete_post_info
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

        prev_post = SBPost(content='test', sb_id=post_info_dict['post_uuid'])
        prev_post.save()
        post = save_post(post_uuid=post_info_dict['post_uuid'],
                         content='test post',
                         current_pleb=self.pleb.email,
                         wall_pleb=self.pleb.email)
        self.assertFalse(post)

    def test_edit_post(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', sb_id=uuid,
                           last_edited_on=datetime.now(pytz.utc),
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email)
        test_post.save()
        edited_post = edit_post_info(content='post edited', post_uuid=uuid,
                                     current_pleb=self.pleb.email)

        self.assertEqual(test_post.sb_id, uuid)
        self.assertTrue(edited_post)

    def test_delete_post(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', sb_id=uuid,
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email)
        test_post.save()
        if delete_post_info(uuid):
            try:
                post = SBPost.nodes.get(sb_id=uuid)
            except SBPost.DoesNotExist:
                return

    def test_edit_post_to_be_deleted(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', sb_id=uuid,
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
        test_post = SBPost(content='test', sb_id=uuid,
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email)
        test_post.save()

        edited_post = edit_post_info(content='test', post_uuid=uuid,
                                     current_pleb=self.pleb.email)

        self.assertEqual(edited_post['detail'], 'content is the same')

    def test_edit_post_same_timestamp(self):
        uuid = str(uuid1())
        edit_time = datetime.now(pytz.UTC)
        test_post = SBPost(content='test', sb_id=uuid,
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
        test_post = SBPost(content='test', sb_id=uuid,
                           current_pleb=self.pleb.email,
                           wall_pleb=self.pleb.email,
                           last_edited_on=future_edit)
        test_post.save()

        edited_post = edit_post_info(content='post edited',
                                     post_uuid=uuid,
                                     last_edited_on=datetime.now(pytz.utc),
                                     current_pleb=self.pleb.email)

        self.assertEqual(edited_post['detail'], 'last edit more recent')