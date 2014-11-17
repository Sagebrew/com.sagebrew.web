from django.shortcuts import redirect, HttpResponseRedirect
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_base.utils import defensive_exception


class TestDefensiveExceptionUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_exception_return_redirect(self):
        exception = Exception("This is my exception")
        res = defensive_exception("test_exception", exception,
                                  redirect("404_Error"))

        self.assertIsInstance(res, HttpResponseRedirect)

    def test_exception_return_boolean(self):
        exception = Exception("This is my exception")
        res = defensive_exception("test_exception", exception, False)

        self.assertFalse(res)

    def test_exception_return_dict(self):
        exception = Exception("This is my exception")
        test_dict = {"hello": "world"}
        res = defensive_exception("test_exception", exception, test_dict)

        self.assertEqual(res, test_dict)

    def test_exception_return_object(self):
        exception = Exception("This is my exception")
        res = defensive_exception("test_exception", exception, self.pleb)

        self.assertEqual(self.pleb.email, res.email)