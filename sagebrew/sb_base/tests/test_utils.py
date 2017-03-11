from django.shortcuts import redirect, HttpResponseRedirect
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import db

from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_base.utils import defensive_exception, NeoQuerySet
from sagebrew.sb_base.neo_models import SBContent


class TestNeoQuerySet(TestCase):
    def setUp(self):
        query = 'MATCH (a) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        for content in range(0, 50):
            SBContent(content="this is content number %d" % content).save()

    def test_get_list(self):
        queryset = NeoQuerySet(SBContent)
        generated_list = list(queryset)
        self.assertEqual(len(generated_list), 50)

    def test_get_spliced_list(self):
        queryset = NeoQuerySet(SBContent).order_by('ORDER BY res.created')
        generated_list = queryset[:5]
        self.assertEqual(len(generated_list), 5)
        self.assertEqual(generated_list[0].content, "this is content number 0")
        self.assertEqual(generated_list[1].content, "this is content number 1")
        self.assertEqual(generated_list[2].content, "this is content number 2")
        self.assertEqual(generated_list[3].content, "this is content number 3")
        self.assertEqual(generated_list[4].content, "this is content number 4")
        generated_list = queryset[20:25]
        self.assertEqual(len(generated_list), 5)
        self.assertEqual(generated_list[0].content, "this is content number 20")
        self.assertEqual(generated_list[1].content, "this is content number 21")
        self.assertEqual(generated_list[2].content, "this is content number 22")
        self.assertEqual(generated_list[3].content, "this is content number 23")
        self.assertEqual(generated_list[4].content, "this is content number 24")
        generated_list = queryset[30:40]
        self.assertEqual(len(generated_list), 10)
        self.assertEqual(generated_list[0].content, "this is content number 30")
        self.assertEqual(generated_list[1].content, "this is content number 31")
        self.assertEqual(generated_list[2].content, "this is content number 32")
        self.assertEqual(generated_list[3].content, "this is content number 33")
        self.assertEqual(generated_list[4].content, "this is content number 34")
        self.assertEqual(generated_list[5].content, "this is content number 35")
        self.assertEqual(generated_list[6].content, "this is content number 36")
        self.assertEqual(generated_list[7].content, "this is content number 37")
        self.assertEqual(generated_list[8].content, "this is content number 38")
        self.assertEqual(generated_list[9].content, "this is content number 39")

    def test_get_spliced_list_reverse(self):
        queryset = NeoQuerySet(SBContent, descending=True)\
            .order_by('ORDER BY res.created')
        generated_list = queryset[:5]
        self.assertEqual(len(generated_list), 5)
        self.assertEqual(generated_list[0].content, "this is content number 49")
        self.assertEqual(generated_list[1].content, "this is content number 48")
        self.assertEqual(generated_list[2].content, "this is content number 47")
        self.assertEqual(generated_list[3].content, "this is content number 46")
        self.assertEqual(generated_list[4].content, "this is content number 45")
        generated_list = queryset[20:25]
        self.assertEqual(len(generated_list), 5)
        self.assertEqual(generated_list[0].content, "this is content number 29")
        self.assertEqual(generated_list[1].content, "this is content number 28")
        self.assertEqual(generated_list[2].content, "this is content number 27")
        self.assertEqual(generated_list[3].content, "this is content number 26")
        self.assertEqual(generated_list[4].content, "this is content number 25")
        generated_list = queryset[40:50]
        self.assertEqual(len(generated_list), 10)
        self.assertEqual(generated_list[0].content, "this is content number 9")
        self.assertEqual(generated_list[1].content, "this is content number 8")
        self.assertEqual(generated_list[2].content, "this is content number 7")
        self.assertEqual(generated_list[3].content, "this is content number 6")
        self.assertEqual(generated_list[4].content, "this is content number 5")
        self.assertEqual(generated_list[5].content, "this is content number 4")
        self.assertEqual(generated_list[6].content, "this is content number 3")
        self.assertEqual(generated_list[7].content, "this is content number 2")
        self.assertEqual(generated_list[8].content, "this is content number 1")
        self.assertEqual(generated_list[9].content, "this is content number 0")

    def test_get_count_with_order(self):
        queryset = NeoQuerySet(SBContent).order_by('ORDER BY res.created')
        self.assertEqual(queryset.count(), 50)

    def test_get_count_without_order(self):
        queryset = NeoQuerySet(SBContent)
        self.assertEqual(queryset.count(), 50)

    def test_get_count_without_order_filter(self):
        for content in range(0, 10):
            SBContent(content="this is content number 2-%d" % content,
                      to_be_deleted=True).save()
        queryset = NeoQuerySet(SBContent)\
            .filter("WHERE res.to_be_deleted=False")
        self.assertEqual(queryset.count(), 50)

    def test_get_list_with_filter(self):
        for content in range(0, 3):
            SBContent(content="this is content number 2-%d" % content,
                      to_be_deleted=True).save()
        queryset = NeoQuerySet(SBContent) \
            .filter("WHERE res.to_be_deleted=True")\
            .order_by('ORDER BY res.created')
        query_res = list(queryset)
        self.assertEqual(queryset.count(), 3)
        self.assertEqual(query_res[0].content, "this is content number 2-0")
        self.assertEqual(query_res[1].content, "this is content number 2-1")
        self.assertEqual(query_res[2].content, "this is content number 2-2")

    def test_get_count_with_order_filter_distinct_reversed(self):
        for content in range(0, 15):
            SBContent(content="this is content number 2-%d" % content,
                      to_be_deleted=True).save()
        queryset = NeoQuerySet(SBContent, distinct=True, descending=True)\
            .order_by('ORDER BY res.created')\
            .filter("WHERE res.to_be_deleted=True")
        self.assertEqual(queryset.count(), 15)
        self.assertEqual(queryset[:1][0].content, "this is content number 2-14")


class TestDefensiveExceptionUtil(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def test_exception_return_redirect(self):
        try:
            raise Exception("This is my exception", "testing")
        except Exception as e:
            res = defensive_exception("test_exception", e,
                                      redirect("404_Error"))

        self.assertIsInstance(res, HttpResponseRedirect)

    def test_exception_return_boolean(self):
        try:
            raise Exception("This is my exception", "testing")
        except Exception as e:
            res = defensive_exception("test_exception", e, False)

        self.assertFalse(res)

    def test_exception_return_dict(self):
        try:
            raise Exception("This is my exception", "testing")
        except Exception as e:
            test_dict = {"hello": "world"}
            res = defensive_exception("test_exception", e, test_dict)

        self.assertEqual(res, test_dict)

    def test_exception_return_object(self):
        try:
            raise Exception("This is my exception", "testing")
        except Exception as e:
            res = defensive_exception("test_exception", e, self.pleb)

        self.assertEqual(self.pleb.email, res.email)

    def test_type_error(self):
        try:
            raise TypeError("Hello", "there")
        except TypeError as e:
            test_defense = defensive_exception("this_test", e, True)

        self.assertTrue(test_defense)

    def test_type_error_with_message(self):
        try:
            raise TypeError("Hello", "there")
        except TypeError as e:
            test_defense = defensive_exception("this_test", e, True,
                                               "type error reached")
        self.assertTrue(test_defense)

    def test_type_error_with_dict_message(self):
        try:
            raise TypeError("Hello", "there")
        except TypeError as e:
            test_defense = defensive_exception("this_test", e, True,
                                               {"exception thrower": "tester"})
        self.assertTrue(test_defense)

    def test_without_raise(self):
        exception = TypeError("Hello", "there")
        test_defense = defensive_exception("this_test", exception, True)

        self.assertTrue(test_defense)
