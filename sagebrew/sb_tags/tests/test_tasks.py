from uuid import uuid1

from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.test import APITestCase

from neomodel import db

from sagebrew.sb_registration.utils import create_user_util_test

from sagebrew.sb_questions.neo_models import Question
from sagebrew.sb_tags.tasks import update_tags, add_auto_tags
from sagebrew.sb_tags.neo_models import Tag


class TestAddAutoTagTasks(APITestCase):

    def setUp(self):
        settings.DEBUG = True
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content="Hey I'm a question",
                                 title=str(uuid1()),
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)

    def tearDown(self):
        settings.DEBUG = False
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_auto_tags(self):
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        res = add_auto_tags.apply_async(
            kwargs={
                "object_uuid": self.question.object_uuid,
                "tag_list": [
                    {'tags': {'text': 'political', 'relevance': 0.10201}},
                    {'tags': {'text': 'settings', 'relevance': 0.10201}},
                    {'tags': {'text': 'go', 'relevance': 0.10201}}
                ]})
        self.assertIsInstance(res.result, list)
        query = 'MATCH (a:Question {object_uuid: "%s"})-[:TAGGED_AS]->' \
                '(b:AutoTag) RETURN b' % self.question.object_uuid
        res, _ = db.cypher_query(query)
        self.assertEqual(len(res), 3)
        query = 'MATCH (b:AutoTag {name: "political"}) RETURN b'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (b:AutoTag {name: "settings"}) RETURN b'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (b:AutoTag {name: "go"}) RETURN b'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

    def test_add_auto_tags_no_input(self):
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        res = add_auto_tags.apply_async(
            kwargs={"object_uuid": self.question.object_uuid, "tag_list": []})
        self.assertTrue(res.result)


class TestUpdateTagsTask(APITestCase):

    def setUp(self):
        settings.DEBUG = True
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content="Hey I'm a question",
                                 title=str(uuid1()),
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)

    def tearDown(self):
        settings.DEBUG = False
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_tags(self):
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        econ_tag = Tag(name="economy").save()
        space_tag = Tag(name="space").save()
        res = update_tags.apply_async(
            kwargs={"tags": ["economy", "space"]})
        self.assertIsInstance(res.result, list)
        query = 'MATCH (a:Tag {object_uuid: "%s"}) RETURN a' % (
            econ_tag.object_uuid)
        res, _ = db.cypher_query(query)
        self.assertEqual(res.one['tag_used'], 1)
        query = 'MATCH (a:Tag {object_uuid: "%s"}) RETURN a' % (
            space_tag.object_uuid)
        res, _ = db.cypher_query(query)
        self.assertEqual(res.one['tag_used'], 1)

    def test_update_tags_no_input(self):
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        res = update_tags.apply_async(
            kwargs={"tags": []})
        self.assertEqual(res.result, [])
