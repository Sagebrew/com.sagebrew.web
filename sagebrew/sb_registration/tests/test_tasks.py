import time
from uuid import uuid1

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import DoesNotExist

from plebs.neo_models import Pleb

from sb_registration.utils import create_user_util_test
from sb_registration.tasks import (update_interests, store_address,
                                   save_profile_picture)


class TestUpdateInterestsTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        try:
            pleb = Pleb.nodes.get(
                email='suppressionlist@simulator.amazonses.com')
            pleb.delete()
            user = User.objects.get(
                email='suppressionlist@simulator.amazonses.com')
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            self.fake_user = User.objects.create_user(
                first_name='test', last_name='test',
                email='suppressionlist@simulator.amazonses.com',
                password='fakepass',
                username='thisisafakeusername')
            self.fake_user.save()

    def tearDown(self):
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_interest(self):
        data = {
            "username": self.pleb.username,
            "interests": {
                "fiscal": True,
                "social": True,
                "education": True
            }
        }
        res = update_interests.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_update_tag_doesnt_exist(self):
        data = {
            "username": self.pleb.username,
            "interests": {
                "fiscal": True,
                "social": True,
                "this_tag_doesnt_exist": True
            }
        }
        res = update_interests.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_update_interest_pleb_doesnt_exist(self):
        data = {
            "username": "this_username_doesnt_exist",
            "interests": {
                "fiscal": True,
                "social": True,
                "this_tag_doesnt_exist": True
            }
        }
        res = update_interests.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, DoesNotExist)


class TestStoreAddressTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        try:
            pleb = Pleb.nodes.get(
                email='suppressionlist@simulator.amazonses.com')
            pleb.delete()
            user = User.objects.get(
                email='suppressionlist@simulator.amazonses.com')
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            self.fake_user = User.objects.create_user(
                first_name='test', last_name='test',
                email='suppressionlist@simulator.amazonses.com',
                password='fakepass',
                username='thisisafakeusername')
            self.fake_user.save()

    def tearDown(self):
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False

    def test_store_address(self):
        data = {
            "username": self.pleb.username,
            "address_clean": {
                "primary_address": "123 Fake Rd.",
                "street_additional": "",
                "city": "Fake City",
                "state": "Mi",
                "postal_code": "11111",
                "latitude": 11.1111,
                "longitude": 11.1111,
                "congressional_district": 1
            }
        }
        res = store_address.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_store_address_pleb_does_not_exist(self):
        data = {
            "username": "this_user_does_not_exist",
            "address_clean": {
                "primary_address": "123 Fake Rd.",
                "street_additional": "",
                "city": "Fake City",
                "state": "Mi",
                "postal_code": "11111",
                "latitude": 11.1111,
                "longitude": 11.1111,
                "congressional_district": 1
            }
        }
        res = store_address.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, DoesNotExist)


class TestSaveProfilePictureTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        try:
            pleb = Pleb.nodes.get(
                email='suppressionlist@simulator.amazonses.com')
            pleb.delete()
            user = User.objects.get(
                email='suppressionlist@simulator.amazonses.com')
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            self.fake_user = User.objects.create_user(
                first_name='test', last_name='test',
                email='suppressionlist@simulator.amazonses.com',
                password='fakepass',
                username='thisisafakeusername')
            self.fake_user.save()

    def tearDown(self):
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False

    def test_save_profile_picture(self):
        data = {
            "username": self.pleb.username,
            "url": "https://www.example.com/"
        }
        res = save_profile_picture.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_save_profile_picture_pleb_does_not_exist(self):
        data = {
            "username": "this_username_does_not_exist",
            "url": "https://www.example.com/"
        }
        res = save_profile_picture.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, DoesNotExist)
