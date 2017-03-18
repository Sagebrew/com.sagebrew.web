from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_posts.neo_models import Post
from sagebrew.sb_questions.neo_models import Question
from sagebrew.sb_uploads.neo_models import UploadedObject
from sagebrew.sb_base.neo_models import (
    get_parent_votable_content, VotableContent,
    get_parent_titled_content, TitledContent)


class TestVotableContentNeoModel(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
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

    def test_vote_content_change_vote_negative(self):
        rel = self.post.votes.connect(self.pleb)
        rel.vote_type = False
        rel.save()

        res = self.post.vote_content(2, self.pleb)
        rel = self.post.votes.relationship(self.pleb)
        self.assertFalse(rel.active)
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


class TestGetParentVotableContent(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content='test',
                                 owner_username=self.pleb.username,
                                 wall_owner_username=self.pleb.username,
                                 title=str(uuid1())).save()
        self.question.owned_by.connect(self.pleb)

    def test_get_parent_votable_content(self):
        res = get_parent_votable_content(self.question.object_uuid)
        self.assertEqual(res, VotableContent.nodes.get(
            object_uuid=self.question.object_uuid))


class TestGetUploadedObject(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.post = Post(content='test', owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username).save()
        self.post.owned_by.connect(self.pleb)
        self.uploaded_object = UploadedObject(url='www.example.com',
                                              height=300, width=300).save()
        self.post.uploaded_objects.connect(self.uploaded_object)

    def test_get_uploaded_object(self):
        res = self.post.get_uploaded_objects()
        self.assertEqual(res[0][0]['url'], self.uploaded_object.url)

    def test_get_uploaded_object_no_objects(self):
        self.post.uploaded_objects.disconnect(self.uploaded_object)
        res = self.post.get_uploaded_objects()
        self.assertFalse(res)


class TestGetParentTitledContent(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.question = Question(title=str(uuid1()),
                                 content="test content").save()

    def test_get_parent_titled_content(self):
        res = get_parent_titled_content(self.question.object_uuid)
        self.assertIsInstance(res, TitledContent)

    def test_get_parent_titled_content_object_does_not_exist(self):
        res = get_parent_titled_content(str(uuid1()))
        self.assertIsInstance(res, AttributeError)
