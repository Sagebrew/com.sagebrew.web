import logging
from uuid import uuid1
from datetime import datetime
from django.test import TestCase

from sb_posts.utils import save_post
from sb_posts.neo_models import SBPost

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
