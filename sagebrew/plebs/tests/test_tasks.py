import us
import time
import pytz
import requests_mock
from uuid import uuid1
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.exceptions import APIException

from neomodel import db
from boto.dynamodb2.table import Table

from api.utils import wait_util
from plebs.neo_models import Pleb, Address
from sb_locations.neo_models import Location
from sb_docstore.utils import connect_to_dynamo, get_table_name
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from plebs.tasks import (create_wall_task,
                         create_friend_request_task,
                         determine_pleb_reps, finalize_citizen_creation,
                         update_reputation, connect_to_state_districts)
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


class TestCreateFriendRequestTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb1 = create_user_util_test(self.email)
        self.user1 = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_friend_request_task_success(self):
        data = {
            'from_username': self.pleb1.email,
            'to_username': self.pleb2.email,
            'object_uuid': str(uuid1())
        }
        res = create_friend_request_task.apply_async(kwargs=data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_create_friend_request_task_failure_pleb_does_not_exist(self):
        data = {
            'from_username': 'totallyfakepleb@gmail.com',
            'to_username': self.pleb2.email,
            'object_uuid': str(uuid1())
        }
        res = create_friend_request_task.apply_async(kwargs=data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertIsInstance(res, Exception)


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


class TestCreateStateDistricts(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_state_districts(self):
        mi = Location(name=us.states.lookup(
            "MI").name, sector="federal").save()
        address = Address(state="MI", latitude=42.532020,
                          longitude=-83.496500).save()
        lower = Location(name='38', sector='state_lower').save()
        upper = Location(name='15', sector='state_upper').save()
        mi.encompasses.connect(lower)
        lower.encompassed_by.connect(mi)
        mi.encompasses.connect(upper)
        upper.encompassed_by.connect(mi)
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertTrue(res.result)
        self.assertTrue(lower in address.encompassed_by)
        self.assertTrue(upper in address.encompassed_by)
        mi.delete()
        address.delete()
        upper.delete()
        lower.delete()

    def test_create_state_districts_already_exist(self):
        mi = Location(name=us.states.lookup(
            "MI").name, sector="federal").save()
        address = Address(state="MI", latitude=42.532020,
                          longitude=-83.496500).save()
        upper = Location(name="15", sector="state_upper").save()
        lower = Location(name="38", sector="state_lower").save()
        address.encompassed_by.connect(lower)
        address.encompassed_by.connect(upper)
        mi.encompasses.connect(upper)
        upper.encompassed_by.connect(mi)
        mi.encompasses.connect(lower)
        lower.encompassed_by.connect(mi)
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertTrue(res.result)
        query = 'MATCH (l:Location {name:"38", sector:"state_lower"}), ' \
                '(l2:Location {name:"15", sector:"state_upper"}) RETURN l, l2'
        res, _ = db.cypher_query(query)
        lower = Location.inflate(res[0].l)
        upper = Location.inflate(res[0].l2)
        self.assertTrue(lower in address.encompassed_by)
        self.assertTrue(upper in address.encompassed_by)
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertTrue(res.result)
        query = 'MATCH (l:Location {name:"38", sector:"state_lower"}), ' \
                '(l2:Location {name:"15", sector:"state_upper"}) RETURN l, l2'
        res, _ = db.cypher_query(query)
        self.assertEqual(len(res[0]), 2)  # assert only two nodes returned
        self.assertEqual(lower, Location.inflate(res[0].l))
        # assert only one lower node
        self.assertEqual(upper, Location.inflate(res[0].l2))
        # assert only one upper node
        mi.delete()
        address.delete()
        upper.delete()
        lower.delete()

    def test_address_doesnt_exist(self):
        res = connect_to_state_districts.apply_async(
            kwargs={"object_uuid": str(uuid1())})
        self.assertIsInstance(res.result, Exception)

    def test_address_has_no_lat_long(self):
        mi = Location(name=us.states.lookup(
            "MI").name, sector="federal").save()
        address = Address(state="MI").save()
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertFalse(res.result)
        mi.delete()
        address.delete()

    def test_address_has_lat_long_outside_usa(self):
        mi = Location(name=us.states.lookup(
            "MI").name, sector="federal").save()
        # lat/long of Greenwich UK
        address = Address(state="MI", latitude=51.4800,
                          longitude=0.0000).save()
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertTrue(res.result)
        mi.delete()
        address.delete()


class TestFinalizeCitizen(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.intercom_url = "https://api.intercom.io/admins"
        self.admin_data = {
            "type": "admin.list",
            "admins": [
                {
                    "type": "admin",
                    "id": 69989,
                    "name": "Devon Bleibtrey",
                    "email": "devon@sagebrew.com"
                }
            ]
        }

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    @requests_mock.mock()
    def test_valid_username(self, m):
        m.get(self.intercom_url, json=self.admin_data,
              status_code=status.HTTP_200_OK)
        self.pleb.initial_verification_email_sent = False
        self.pleb.save()
        res = finalize_citizen_creation.apply_async(
            kwargs={'username': self.pleb.username})
        self.assertTrue('add_object_to_search_index' in res.result)
        self.assertTrue('check_privileges_task' in res.result)
        self.assertTrue(Pleb.get(
            username=self.pleb.username, cache_buster=True
        ).initial_verification_email_sent)

    @requests_mock.mock()
    def test_bad_admin(self, m):
        bad_admin_data = {
            "type": "admin.list",
            "admins": [
                {
                    "type": "admin",
                    "id": 55555,
                    "name": "Devon Bleibtrey",
                    "email": "devon@sagebrew.com"
                }
            ]
        }
        m.get(self.intercom_url, json=bad_admin_data,
              status_code=status.HTTP_200_OK)
        self.pleb.initial_verification_email_sent = False
        self.pleb.save()
        res = finalize_citizen_creation.apply_async(
            kwargs={'username': self.pleb.username})
        self.assertFalse(Pleb.get(
            username=self.pleb.username, cache_buster=True
        ).initial_verification_email_sent)
        self.assertIsInstance(res.result, APIException)
