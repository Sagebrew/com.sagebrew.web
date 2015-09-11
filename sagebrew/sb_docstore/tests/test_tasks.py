import time
import pytz
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import db

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question

from sb_docstore.utils import add_object_to_table
from sb_docstore.tasks import spawn_user_updates, add_object_to_table_task


class TestSpawnUserUpdates(TestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(title="testing spawn user updates with "
                                       "questions?").save()
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_spawn_user_updates(self):
        data = {
            "username": self.pleb.username,
            "object_uuids": [self.question.object_uuid]
        }
        res = spawn_user_updates.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res)

    def test_spawn_user_updates_with_votes(self):
        now = unicode(datetime.now(pytz.utc))

        vote_data = {
            'parent_object': self.question.object_uuid,
            'user': self.pleb.username,
            'status': 1,
            'created': now
        }
        data = {
            "username": self.pleb.username,
            "object_uuids": [self.question.object_uuid]
        }
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)

        res = spawn_user_updates.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)


class TestAddObjectToTableTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question().save()
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_object_to_table(self):
        data = {
            "object_data": {
                "parent_object": self.question.object_uuid,
                "user": self.pleb.username,
                "status": 1,
                "created": unicode(datetime.now(pytz.utc))
            },
            "table_name": "votes"
        }
        res = add_object_to_table_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
