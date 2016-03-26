from uuid import uuid1
import time

from django.core import signing
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from api.utils import (add_failure_to_queue,
                       encrypt, decrypt, generate_short_token,
                       generate_long_token, smart_truncate,
                       gather_request_data, flatten_lists,
                       calc_stripe_application_fee, clean_url,
                       empty_text_to_none, generate_summary)
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

'''
class TestCreateAutoTags(TestCase):
    def test_create_auto_tags(self):
        res = create_auto_tags("This is some test content")

        self.assertEqual(res['status'], 'OK')
        self.assertEqual(res['keywords'], [{'relevance': '0.965652',
                                            'text': 'test content'}])
'''


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
        res = create_user_util_test(self.email, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.title = str(uuid1())
        self.question = Question(content=str(uuid1()),
                                 title=self.title,
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)

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


class TestFlattenList(TestCase):

    def test_flatten(self):
        lists = [1, 1, 2, 3, [1, 2, 3], [1]]
        res = flatten_lists(lists)
        self.assertEqual(list(res), [1, 1, 2, 3, 1, 2, 3, 1])

    def test_flatten_strings(self):
        lists = ['this', 'is', 'a', ['test', ['list', 'thing']], 'test']
        res = flatten_lists(lists)
        self.assertEqual(list(res), ['this', 'is', 'a', 'test', 'list',
                                     'thing', 'test'])


class TestCalcStripeApplicationFee(TestCase):

    def setUp(self):
        self.amount = 500
        self.application_fee = settings.STRIPE_FREE_ACCOUNT_FEE

    def test_amount(self):
        res = calc_stripe_application_fee(self.amount, self.application_fee)
        self.assertEqual(
            res, int(self.amount *
                     (self.application_fee +
                      settings.STRIPE_TRANSACTION_PERCENT) + 30))

    def test_amount_multiple_donations(self):
        res = calc_stripe_application_fee(self.amount, self.application_fee, 4)
        self.assertEqual(
            res, int(self.amount *
                     (self.application_fee +
                      settings.STRIPE_TRANSACTION_PERCENT) + (4 * 30)))


class TestCleanUrl(TestCase):

    def test_empty_url(self):
        res = clean_url("")
        self.assertIsNone(res)

    def test_none(self):
        res = clean_url(None)
        self.assertIsNone(res)

    def test_no_http(self):
        url = "www.google.com"
        res = clean_url(url)
        self.assertEqual(res, "http://%s" % url)

    def test_with_http(self):
        url = "http://www.google.com"
        res = clean_url(url)
        self.assertEqual(res, url)

    def test_with_https(self):
        url = "https://www.google.com"
        res = clean_url(url)
        self.assertEqual(res, url)

    def test_with_https_and_padding(self):
        url = "   https://www.google.com   "
        res = clean_url(url)
        self.assertEqual(res, "https://www.google.com")

    def test_with_http_and_padding(self):
        url = "   http://www.google.com   "
        res = clean_url(url)
        self.assertEqual(res, "http://www.google.com")


class TestEmptyTextToNone(TestCase):

    def test_no_text(self):
        res = empty_text_to_none("")
        self.assertIsNone(res)

    def test_text(self):
        text = "hello world this is great"
        res = empty_text_to_none(text)
        self.assertEqual(res, text)

    def test_text_with_padding(self):
        text = "    hello world this is great      "
        res = empty_text_to_none(text)
        self.assertEqual(res, "hello world this is great")

    def test_none(self):
        res = empty_text_to_none(None)
        self.assertIsNone(res)


class TestGenerateSummary(TestCase):

    def test_no_text(self):
        res = generate_summary("")
        self.assertEqual("", res)

    def test_short_text(self):
        text = "hello world this is great"
        res = generate_summary("hello world this is great")
        self.assertEqual(res, text)

    def test_multi_sentence_summary(self):
        text = "Wow, I really can't believe it. " \
               "It's 2015 and I just stumbled over this. " \
               "I need Visual Studio 2010 compatible compilation for x64 to " \
               "build Python 3 extensions. " \
               "It seems this is absolutely impossible now without going " \
               "back to a Windows that is never updated. " \
               "Very disappointing. " \
               "I originally tried to fix this issue: " \
               "http://stackoverflow.com/questions/10888391/error-link-fatal" \
               "-error-lnk1123-failure-during-conversion-to-coff-file-inval " \
               "(I only have the SDK installed, no Visual Studio) and " \
               'installed the "Visual C++ 2010 SP1 Compiler Update" for ' \
               'that, and now I have this stupid header issue which is not ' \
               'going to be fixed. Why does compiling under Windows always ' \
               'have to be such a massive pain?'
        res = generate_summary(text)
        self.assertIn("visual studio", res.lower())

    def test_none(self):
        res = generate_summary(None)
        self.assertEqual(res, "")
