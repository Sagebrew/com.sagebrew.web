import time
import pytz
from uuid import uuid1
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User

from boto.dynamodb2.table import Table

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_docstore.utils import connect_to_dynamo, get_table_name
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from plebs.tasks import (create_wall_task,
                         determine_pleb_reps, finalize_citizen_creation,
                         update_reputation)
from sb_wall.neo_models import Wall


class TestCreateWallTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        try:
            pleb = Pleb.nodes.get(
                email='suppressionlist@simulator.amazonses.com',
                username="thisthat")
            pleb.delete()
            user = User.objects.get(
                email='suppressionlist@simulator.amazonses.com',
                username="thisthat")
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            pass
        self.fake_user = User.objects.create_user(
            first_name='test', last_name='test',
            email='suppressionlist@simulator.amazonses.com',
            password='fakepass',
            username='thisisafakeusername')
        self.fake_user.save()
        self.fake_pleb = Pleb(email=self.fake_user.email,
                              username=self.fake_user.username).save()

    def tearDown(self):
        self.fake_pleb.delete()
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_wall_task_success(self):
        task_data = {
            'username': self.fake_user.username
        }
        res = create_wall_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))

    def test_create_wall_task_pleb_has_wall(self):
        wall = Wall(wall_id=str(uuid1())).save()
        wall.owned_by.connect(self.fake_pleb)
        self.fake_pleb.wall.connect(wall)
        task_data = {
            'username': self.fake_user.username,
        }

        res = create_wall_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))


class TestDeterminePlebReps(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_determine_pleb_reps(self):
        data = {
            'username': self.pleb.username
        }
        res = determine_pleb_reps.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)


class TestUpdateReputation(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_reputation(self):
        data = {
            "username": self.pleb.username
        }
        res = update_reputation.apply_async(kwargs=data)
        self.assertTrue(res.result)

    def test_updated_rep(self):
        self.pleb.reputation_update_seen = True
        self.pleb.save()
        question = Question(title=str(uuid1()), content="some test content",
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        conn = connect_to_dynamo()
        votes_table = Table(table_name=get_table_name('votes'),
                            connection=conn)
        votes_table.put_item(data={"parent_object": question.object_uuid,
                                   "status": 1,
                                   "now": str(datetime.now(pytz.utc)),
                                   "user": self.user2.username})
        cache.clear()
        data = {
            "username": self.pleb.username
        }
        update_reputation.apply_async(kwargs=data)
        pleb = Pleb.nodes.get(username=self.pleb.username)
        self.assertFalse(pleb.reputation_update_seen)
        self.assertEqual(pleb.reputation, 5)

    def test_pleb_doesnt_exist(self):
        data = {
            "username": str(uuid1())
        }
        res = update_reputation.apply_async(kwargs=data)
        self.assertIsInstance(res.result, Exception)


class TestFinalizeCitizen(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_valid_username(self):
        res = finalize_citizen_creation.apply_async(
            kwargs={'username': self.pleb.username})
        self.assertTrue('add_object_to_search_index' in res.result)
        self.assertTrue('check_privileges_task' in res.result)
