from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_posts.neo_models import SBPost
from sb_base.neo_models import SBContent


class TestSBVoteableContentNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
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

class TestSBContentNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.content = SBContent(content='test', sb_id=str(uuid1())).save()
        self.post = SBPost(content='fake content', sb_id=str(uuid1())).save()

    def test_create_relations(self):
        res = self.content.create_relations(self.pleb)

        self.assertTrue(res)

    def test_delete_content(self):
        res = self.content.delete_content(self.pleb)

        self.assertIsInstance(res, SBContent)

    def test_flag_content_unavailable_flag(self):
        res = self.post.flag_content('changed', self.pleb)

        self.assertFalse(res)

    def test_flag_content_user_already_flagged(self):
        self.post.flagged_by.connect(self.pleb)
        res = self.post.flag_content('spam', self.pleb)

        self.assertIsInstance(res, SBPost)


class TestSBNonVersionedContent(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post = SBPost(content='fake content', sb_id=str(uuid1())).save()

    def test_edit_content(self):
        res = self.post.edit_content('test edit', self.pleb)

        self.assertIsInstance(res, SBPost)
        self.assertEqual(res.content, 'test edit')
