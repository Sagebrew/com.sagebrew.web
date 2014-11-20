from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment


class TestSBCommentsNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.comment = SBComment(content='test content', sb_id=str(uuid1())).\
            save()
        self.comment.is_owned_by.connect(self.pleb)

    def test_get_comment_dict(self):
        res = self.comment.get_comment_dict(self.pleb)

        self.assertIsInstance(res, dict)
