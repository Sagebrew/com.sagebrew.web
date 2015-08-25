from django.core import signing
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from api.utils import (add_failure_to_queue,
                       encrypt, decrypt, generate_short_token,
                       generate_long_token, create_auto_tags, smart_truncate)


class TestAddFailureToQueue(TestCase):
    def setUp(self):
        self.message = {
            'message': 'this is a test message to add if a task fails'
        }

    def test_adding_failure_to_queue(self):
        self.assertTrue(add_failure_to_queue(self.message))


class TestEncryptAndDecrypt(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_encrypt(self):
        res = encrypt("some test data")
        self.assertEqual("some test data", signing.loads(res))

    def test_decrypt(self):
        test_data = "some test data"
        encrypted = signing.dumps(test_data)
        res = decrypt(encrypted)
        self.assertEqual("some test data", res)

    def test_generate_short_token(self):
        res = generate_short_token()
        self.assertIsNotNone(res)

    def test_generate_long_token(self):
        res = generate_long_token()
        self.assertIsNotNone(res)


class TestCreateAutoTags(TestCase):
    def test_create_auto_tags(self):
        res = create_auto_tags("This is some test content")

        self.assertEqual(res['status'], 'OK')
        self.assertEqual(res['keywords'], [{'relevance': '0.965652',
                                            'text': 'test content'}])


class TestSmartTruncate(TestCase):
    def test_smart_truncate(self):
        res = smart_truncate("this is some test content which is longer than "
                             "100 characters to determine if the logic in "
                             "this function actually works")
        self.assertEqual(res, "this is some test content which is longer "
                              "than 100 characters to determine if the "
                              "logic in this...")

    def test_smart_truncate_short(self):
        res = smart_truncate("this is a short truncate")
        self.assertEqual(res, "this is a short truncate")

    def test_custom_truncate_suffix(self):
        res = smart_truncate("this is some test content which is longer than "
                             "100 characters to determine if the logic in "
                             "this function actually works", suffix="WOOOO")
        self.assertEqual(res, "this is some test content which is longer "
                              "than 100 characters to determine if the "
                              "logic in thisWOOOO")
