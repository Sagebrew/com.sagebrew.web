from uuid import uuid1
import time
import pytz
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_questions.neo_models import Question

from sagebrew.sb_docstore.utils import add_object_to_table
from sagebrew.sb_docstore.tasks import spawn_user_updates, add_object_to_table_task


class TestSpawnUserUpdates(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(title=str(uuid1())).save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_spawn_user_updates(self):
        data = {
            "username": self.pleb.username,
            "object_uuid": self.question.object_uuid
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
            "object_uuid": self.question.object_uuid
        }
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)

        res = spawn_user_updates.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)


class TestAddObjectToTableTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(title=str(uuid1())).save()

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
