from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question


class TestQuestionNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content='test content',
                                 object_uuid=str(uuid1()),
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)

    def test_add_auto_tags(self):
        auto_tags = [{'tags': {'text': 'testautotag', 'relevance': 0.10201}}]
        res = self.question.add_auto_tags(auto_tags)

        self.assertIsInstance(res, list)

    def test_empty_get_tags_string(self):
        res = self.question.get_tags_string()

        self.assertEqual(res, "")

    def test_empty_get_one_tag_string(self):
        tag = Tag(name=str(uuid1())).save()
        self.question.tags.connect(tag)
        res = self.question.get_tags_string()
        self.question.tags.disconnect(tag)
        self.assertEqual(res, "%s" % tag.name)

    def test_empty_get_multiple_tag_string(self):
        tag = Tag(name=str(uuid1())).save()
        tag2 = Tag(name=str(uuid1())).save()
        self.question.tags.connect(tag)
        self.question.tags.connect(tag2)
        res = self.question.get_tags_string()
        self.question.tags.disconnect(tag)
        self.question.tags.disconnect(tag2)
        self.assertIn(tag.name, res)
        self.assertIn(tag2.name, res)
        self.assertIn(',', res)
