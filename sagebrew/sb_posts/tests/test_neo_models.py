import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_posts.neo_models import SBPost

class TestSBPostNeoModels(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post = SBPost(content='test', sb_id=str(uuid1())).save()
        self.post.owned_by.connect(self.pleb)

    def test_create_relations(self):
        res = self.post.create_relations(self.pleb,
                                         wall=self.pleb.wall.all()[0])

        self.assertFalse(isinstance(res, Exception))

    def test_get_post_dictionary(self):
        res = self.post.get_post_dictionary(self.pleb)

        self.assertIsInstance(res, dict)

    def test_render_post_wall_html(self):
        res = self.post.render_post_wall_html(self.pleb)

        self.assertTrue(res)