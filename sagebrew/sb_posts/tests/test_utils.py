import logging
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_posts.utils import save_post, get_pleb_posts
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

logger = logging.getLogger('loggly_logs')


class TestSavePost(TestCase):
    def test_save_post(self):
        uuid = str(uuid1())
        post = save_post(post_uuid=uuid, content="test post",
                         created=datetime.now())

        self.assertIsNot(post, False)

    def test_post_already_exists(self):
        post_info_dict = {'content': 'test post',
                          'post_uuid': str(uuid1())}

        prev_post = SBPost(content='test', object_uuid=post_info_dict['post_uuid'])
        prev_post.save()
        post = save_post(post_uuid=post_info_dict['post_uuid'],
                         content='test post', created=datetime.now())
        self.assertIsInstance(post, SBPost)


class TestGetPlebPostsUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_pleb_posts(self):
        res = get_pleb_posts(self.pleb, '5')

        self.assertFalse(isinstance(res, Exception))