from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_comments.neo_models import SBComment


class TestSBCommentsNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.comment = SBComment(content='test content', object_uuid=str(uuid1())).\
            save()
        self.comment.owned_by.connect(self.pleb)

    def test_get_single_dict(self):
        res = self.comment.get_single_dict(self.pleb)

        self.assertIsInstance(res, dict)
