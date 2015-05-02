from django.shortcuts import redirect, HttpResponseRedirect
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_base.utils import defensive_exception


class TestDefensiveExceptionUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
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
