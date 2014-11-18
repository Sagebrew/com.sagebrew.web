import logging
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_posts.utils import save_post, get_pleb_posts
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

logger = logging.getLogger('loggly_logs')

class TestSavePost(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_save_post(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         current_pleb=self.pleb.email,
                         wall_pleb=self.pleb.email)

        self.assertIsNot(post, False)


    def test_post_already_exists(self):
        # TODO changed the response for an already existing post to True
        # Does this screw any other functionality?
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
        self.assertTrue(post)

    def test_save_post_no_uuid(self):
        post = save_post(self.pleb.email, self.pleb.email, 'testcontent')

        self.assertIsInstance(post, SBPost)

    def test_save_post_pleb_does_not_exist(self):
        post = save_post(self.pleb.email, 'fakeemail@fake.com', 'testsasdfass')

        self.assertIsInstance(post, Exception)


class TestGetPlebPostsUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_pleb_posts(self):
        res = get_pleb_posts(self.pleb, '5')

        self.assertFalse(isinstance(res, Exception))