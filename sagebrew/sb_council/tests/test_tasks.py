import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_flags.neo_models import Flag
from sb_questions.neo_models import Question

from sb_council.tasks import (update_closed_task,
                              check_closed_reputation_changes_task)


class TestUpdateClosedTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.flag = Flag().save()
        self.question = Question().save()
        self.question.flags.connect(self.flag)
        self.vote_rel = self.question.council_votes.connect(self.pleb)
        self.vote_rel.active = True
        self.vote_rel.vote_type = True
        self.vote_rel.save()
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_updated_closed(self):
        task_data = {'object_uuid': self.question.object_uuid}

        res = update_closed_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertFalse(isinstance(res.result, Exception))
        self.question.refresh()
        self.assertTrue(self.question.is_closed)


class TestCheckClosedReputationChangesTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.flag = Flag().save()
        self.question = Question().save()
        self.question.flags.connect(self.flag)
        self.vote_rel = self.question.council_votes.connect(self.pleb)
        self.vote_rel.active = True
        self.vote_rel.vote_type = True
        self.vote_rel.save()
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_check_closed_reputation_changes(self):
        res = check_closed_reputation_changes_task.apply_async()
        while not res.ready():
            time.sleep(1)
        self.assertFalse(isinstance(res.result, Exception))
