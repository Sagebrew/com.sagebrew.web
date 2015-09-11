import time

from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from neomodel import db

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_questions.neo_models import Question
from sb_questions.tasks import (add_auto_tags_to_question_task,
                                add_question_to_indices_task,
                                update_search_index)


class TestAddQuestionToIndicesTask(TestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(object_uuid=str(uuid1()),
                                 title=str(uuid1())).save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_question_to_indices_task(self):
        data = {
            "question": {
                "object_uuid": self.question.object_uuid,
                "content": self.question.content,
                "owner_username": self.pleb.username
            }
        }
        res = add_question_to_indices_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_add_question_to_indices_task_already_added(self):
        data = {
            "question": {
                "object_uuid": self.question.object_uuid,
                "content": self.question.content,
                "owner_username": self.pleb.username
            }
        }
        self.question.added_to_search_index = True
        self.question.save()
        res = add_question_to_indices_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)


class TestAddAutoTagsToQuestionTask(TestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(object_uuid=str(uuid1()),
                                 content="This is some test content "
                                         "that I just created.",
                                 title=str(uuid1())).save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_auto_tags(self):
        data = {
            'object_uuid': self.question.object_uuid
        }
        res = add_auto_tags_to_question_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertNotIsInstance(res.result, Exception)

    def test_add_auto_tags_question_does_not_exist(self):
        data = {
            'object_uuid': str(uuid1())
        }
        res = add_auto_tags_to_question_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, Exception)


class TestUpdateSearchIndex(TestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(object_uuid=str(uuid1()),
                                 content="This is some test content "
                                         "that I just created.",
                                 owner_username=self.pleb.username,
                                 title="This is a test title").save()
        self.question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(self.question)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_search_index(self):
        data = {
            "object_uuid": self.question.object_uuid
        }
        res = update_search_index.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
