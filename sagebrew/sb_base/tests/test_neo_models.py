from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_posts.neo_models import Post


class TestVotableContentNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username).save()
        self.post.owned_by.connect(self.pleb)

    def test_vote_content(self):
        res = self.post.vote_content(True, self.pleb)

        self.assertIsInstance(res, Post)

    def test_vote_content_already_voted(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = True
        rel.save()

        res = self.post.vote_content(True, self.pleb)

        self.assertIsInstance(res, Post)

    def test_vote_content_change_vote(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = False
        rel.save()

        res = self.post.vote_content(True, self.pleb)

        self.assertIsInstance(res, Post)

    def test_remove_content(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = False
        rel.save()

        res = self.post.remove_vote(rel)

        self.assertIsInstance(res, Post)
