import time
from uuid import uuid1

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from neomodel import db

from sagebrew.sb_registration.utils import create_user_util_test

from sagebrew.sb_questions.neo_models import Question
from sagebrew.sb_questions.tasks import (
    add_auto_tags_to_question_task, create_question_summary_task)


class TestAddAutoTagsToQuestionTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
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


class TestQuestionTasks(TestCase):

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

    def test_summary_question_does_not_exist(self):
        query = 'MATCH (a:Solution) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        bad_uuid = str(uuid1())
        res = create_question_summary_task.apply_async(
            kwargs={"object_uuid": bad_uuid})
        self.assertIsInstance(res.result, Exception)

    def test_summary_question_exists(self):
        content = "My content that needs to be converted into a summary."
        self.question.content = content
        self.question.save()
        res = create_question_summary_task.apply_async(
            kwargs={"object_uuid": self.question.object_uuid})
        self.assertTrue(res.result.summary, content)
