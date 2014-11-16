import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_posts.neo_models import SBPost

class TestSBVoteableContentNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post = SBPost(content='test', sb_id=str(uuid1())).save()
        self.post.owned_by.connect(self.pleb)

    def test_vote_content(self):
        res = self.post.vote_content(True, self.pleb)

        self.assertIsInstance(res, SBPost)

    def test_vote_content_already_voted(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = True
        rel.save()

        res = self.post.vote_content(True, self.pleb)

        self.assertIsInstance(res, SBPost)

    def test_vote_content_change_vote(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = False
        rel.save()

        res = self.post.vote_content(True, self.pleb)

        self.assertIsInstance(res, SBPost)

    def test_remove_content(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = False
        rel.save()

        res = self.post.remove_vote(rel)

        self.assertIsInstance(res, SBPost)

    def test_upvote_count(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = True
        rel.save()

        res = self.post.get_upvote_count()

        self.assertEqual(res, 1)

    def test_downvote_count(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = False
        rel.save()

        res = self.post.get_downvote_count()

        self.assertEqual(res, 1)

    def test_get_vote_count(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = True
        rel.save()

        pleb = Pleb(email=str(uuid1())).save()
        rel2 = self.post.votes.connect(pleb)
        rel2.vote_type = True
        rel2.save()

        res = self.post.get_vote_count()
        
        self.assertEqual(res, 2)