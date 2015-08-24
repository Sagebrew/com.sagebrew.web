from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_posts.neo_models import Post
from sb_questions.neo_models import Question
from sb_uploads.neo_models import UploadedObject
from sb_tags.neo_models import Tag
from sb_base.neo_models import get_parent_votable_content, VotableContent


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

    def test_council_vote(self):
        res = self.post.council_vote(True, self.pleb)
        self.assertIsNotNone(res)

    def test_council_vote_already_vote(self):
        rel = self.post.council_votes.connect(self.pleb)
        rel.vote_type = True
        rel.active = True
        rel.save()
        res = self.post.council_vote(True, self.pleb)
        self.assertIsNotNone(res)


class TestTaggableContent(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content='test', object_uuid=str(uuid1()),
                                 owner_username=self.pleb.username,
                                 wall_owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)
        self.tag = Tag(name="test_tag", base=True).save()

    def test_add_tags(self):
        res = self.question.add_tags("test_tag")
        self.assertEqual(res[0], self.tag)
        self.assertTrue(self.question.tags.is_connected(self.tag))


class TestVersionedContent(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content='test',
                                 owner_username=self.pleb.username,
                                 wall_owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)
        self.tag = Tag(name=str(uuid1())).save()

    def test_get_rep_breakout(self):
        res = self.question.get_rep_breakout()
        self.assertEqual(res['base_tag_list'], [])
        self.assertEqual(res['total_rep'], 0)

    def test_get_rep_breakout_tags(self):
        self.question.tags.connect(self.tag)
        res = self.question.get_rep_breakout()
        self.assertEqual(res['tag_list'], [self.tag.name])
        self.assertEqual(res['total_rep'], 0)


class TestGetParentVotableContent(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content='test',
                                 owner_username=self.pleb.username,
                                 wall_owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)

    def test_get_parent_votable_content(self):
        res = get_parent_votable_content(self.question.object_uuid)
        self.assertEqual(res, VotableContent.nodes.get(
            object_uuid=self.question.object_uuid))


class TestGetUploadedObject(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post = Post(content='test', owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username).save()
        self.post.owned_by.connect(self.pleb)
        self.uploaded_object = UploadedObject(url='www.example.com',
                                              height=300, width=300).save()
        self.post.uploaded_objects.connect(self.uploaded_object)

    def test_get_uploaded_object(self):
        res = self.post.get_uploaded_objects()
        self.assertEqual(res[0]['url'], self.uploaded_object.url)

    def test_get_uploaded_object_no_objects(self):
        self.post.uploaded_objects.disconnect(self.uploaded_object)
        res = self.post.get_uploaded_objects()
        self.assertFalse(res)
