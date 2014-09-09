import time
import pytz
import logging
from datetime import datetime, timedelta
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from sb_posts.utils import save_post, edit_post_info, delete_post_info, \
    create_post_vote, flag_post
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb

logger = logging.getLogger('loggly_logs')

class TestSavePost(TestCase):
    def setUp(self):
        logger.critical("Testing logs in circle Fo sho")
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

    def test_save_post(self):
        poster = Pleb.index.get(email=self.pleb.email)
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.pleb.email,
                         wall_pleb=self.pleb.email)
        wall = post.traverse('posted_on_wall').run()[0]

        self.assertEqual(poster.email,
                         post.traverse('owned_by').run()[0].email)
        self.assertEqual(wall, self.pleb.traverse('wall').run()[0])
        self.assertEqual("test post", post.content)
        self.assertEqual(post.post_id, uuid)
        post.delete()

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
        self.assertEqual(post, None)

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
                post = SBPost.index.get(post_id=uuid)
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
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

    def test_upvote_post(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.pleb.email,
                         wall_pleb=self.pleb.email)
        create_post_vote(pleb=self.pleb.email, post_uuid=post.post_id,
                         vote_type="up")
        time.sleep(1)  # wait for task to finish
        post.refresh()


    def test_downvote_post(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.pleb.email,
                         wall_pleb=self.pleb.email)
        res = create_post_vote(pleb=self.pleb.email, post_uuid=post.post_id,
                         vote_type="down")

        self.assertTrue(res)


    def test_downvote_twice(self):
        uuid = str(uuid1())
        post = SBPost(post_id=uuid, content='test')
        post.save()
        pleb = Pleb.index.get(email=self.pleb.email)
        post.down_voted_by.connect(pleb)
        res = create_post_vote(pleb=self.pleb.email, post_uuid=post.post_id,
                         vote_type="down")

        self.assertFalse(res)


    def test_upvote_twice(self):
        uuid = str(uuid1())
        post = SBPost(post_id=uuid, content='test')
        post.save()
        pleb = Pleb.index.get(email=self.pleb.email)
        post.up_voted_by.connect(pleb)
        res = create_post_vote(pleb=self.pleb.email, post_uuid=post.post_id,
                         vote_type="up")

        self.assertFalse(res)


class TestFlagPost(TestCase):
    def setUp(self):
        self.email = str(uuid1()) + '@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

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
