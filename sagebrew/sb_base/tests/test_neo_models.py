from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_posts.neo_models import Post
from sb_base.neo_models import SBContent


class TestVotableContentNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post = Post(content='test', object_uuid=str(uuid1())).save()
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


class TestSBContentNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.content = SBContent(content='test', object_uuid=str(uuid1())).save()
        self.post = Post(content='fake content', object_uuid=str(uuid1())).save()

    def test_flag_content_unavailable_flag(self):
        res = self.post.flag_content('changed', self.pleb)

        self.assertFalse(res)

    def test_flag_content_user_already_flagged(self):
        self.post.flagged_by.connect(self.pleb)
        res = self.post.flag_content('spam', self.pleb)

        self.assertIsInstance(res, Post)
