import time

from django.core import signing
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from api.utils import (add_failure_to_queue,
                       encrypt, decrypt, generate_short_token,
                       generate_long_token, create_auto_tags, smart_truncate,
                       gather_request_data)
from sb_questions.neo_models import Question


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


class TestGatherRequestData(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.title = "test question title"
        self.question = Question(content="Hey I'm a question",
                                 title=self.title,
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(self.question)

    def test_no_query_params_request(self):
        request = self.factory.get('/conversations/%s/' %
                                   self.question.object_uuid)
        context = {'request': request}
        request, expand, expand_array, relations, expedite = \
            gather_request_data(context)
        self.assertEqual('false', expand)
        self.assertEqual(len(expand_array), 0)
        self.assertEqual('primarykey', relations)
        self.assertEqual('false', expedite)

    def test_explicit_expand(self):
        request = self.factory.get('/conversations/%s/' %
                                   self.question.object_uuid)
        context = {'request': request}
        request, expand, expand_array, relations, expedite = \
            gather_request_data(context, expand_param=True)
        self.assertEqual('true', expand)
        self.assertEqual(len(expand_array), 0)
        self.assertEqual('primarykey', relations)
        self.assertEqual('false', expedite)

    def test_explicit_expedite(self):
        request = self.factory.get('/conversations/%s/' %
                                   self.question.object_uuid)
        context = {'request': request}
        request, expand, expand_array, relations, expedite = \
            gather_request_data(context, expedite_param=True)
        self.assertEqual('false', expand)
        self.assertEqual(len(expand_array), 0)
        self.assertEqual('primarykey', relations)
        self.assertEqual('true', expedite)

    def test_query_params(self):
        request = self.factory.get('/conversations/%s/?'
                                   'expedite=true&expand=true' %
                                   self.question.object_uuid)
        context = {'request': request}
        request, expand, expand_array, relations, expedite = \
            gather_request_data(context, expedite_param=True)
        self.assertEqual('true', expand)
        self.assertEqual(len(expand_array), 0)
        self.assertEqual('primarykey', relations)
        self.assertEqual('true', expedite)
