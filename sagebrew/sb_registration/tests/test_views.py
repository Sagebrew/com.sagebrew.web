import time
import datetime
from uuid import uuid1
from json import loads

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.test import TestCase, RequestFactory, Client
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import call_command
from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status

from api.utils import wait_util
from sb_registration.views import (profile_information,
                                   signup_view_api, logout_view,
                                   login_view, login_view_api,
                                   resend_email_verification,
                                   email_verification, interests)
from sb_registration.models import EmailAuthTokenGenerator
from sb_registration.utils import create_user_util_test
from plebs.neo_models import Pleb, Address


class InterestsTest(TestCase):
    def setUp(self):
        call_command("create_prepopulated_tags")
        time.sleep(3)
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.completed_profile_info = True
        self.pleb.save()

    def test_no_topics_selected(self):
        my_dict = {"fiscal": False, "education": False, "space": False,
                   "drugs": False, "science": False, "energy": False,
                   "environment": False, "defense": False, "health": False,
                   "social": False, "foreign_policy": False,
                   "agriculture": False}
        request = self.factory.post('/registration/interests',
                                    data=my_dict)
        request.user = self.user
        response = interests(request)

        self.assertEqual(response.status_code, 302)

    def test_all_topics_selected(self):
        my_dict = {"fiscal": True, "education": True, "space": True,
                   "drugs": True, "science": True, "energy": True,
                   "environment": True, "defense": True, "health": True,
                   "social": True, "foreign_policy": True,
                   "agriculture": True}
        request = self.factory.post('/registration/interests',
                                    data=my_dict)
        request.user = self.user
        response = interests(request)

        self.assertEqual(response.status_code, 302)

    def test_some_topics_selected(self):
        my_dict = {"fiscal": False, "education": True, "space": False,
                   "drugs": True, "science": True, "energy": True,
                   "environment": False, "defense": True, "health": False,
                   "social": True, "foreign_policy": True,
                   "agriculture": False}
        request = self.factory.post('/registration/interests',
                                    data=my_dict)
        request.user = self.user
        response = interests(request)

        self.assertEqual(response.status_code, 302)

    def test_interests_pleb_does_not_exist(self):
        my_dict = {"fiscal": False, "education": True, "space": False,
                   "drugs": True, "science": True, "energy": True,
                   "environment": False, "defense": True, "health": False,
                   "social": True, "foreign_policy": True,
                   "agriculture": False}
        request = self.factory.post('/registration/interests',
                                    data=my_dict)
        self.user.username = 'fakeusername'
        request.user = self.user
        response = interests(request)

        self.assertEqual(response.status_code, 302)

    def test_random_cat_selected_no_topics_selected(self):
        pass

    def test_random_cat_selected_random_topics_selected(self):
        pass

    def test_no_cat_selected_random_topics_selected(self):
        pass

    def test_get_request(self):
        request = self.factory.get('/registration/interests')
        request.user = self.user
        response = interests(request)

        self.assertEqual(response.status_code, 200)


class TestProfileInfoView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.completed_profile_info = False
        self.pleb.save()
        addresses = Address.nodes.all()
        for address in addresses:
            if self.pleb.address.is_connected(address):
                address.owned_by.disconnect(self.pleb)
                self.pleb.address.disconnect(address)

    def test_user_info_population_no_birthday(self):
        my_dict = {'date_of_birth': [u'']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)

        self.assertIn(response.status_code, [200,302])

    def test_user_info_population_incorrect_birthday(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_zipcode(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_primary(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_country(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_city(self):
        my_dict = {"home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"],
                   "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_valid(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_profile_information_success(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)

        self.assertEqual(response.status_code, 302)

    def test_profile_information_address_not_in_smartystreets(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["127 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"]}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)

        self.assertIn(response.status_code, [200,302])

    def test_profile_information_address_has_no_suggestions(self):
        my_dict = {"city": ["We"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glr"],
                   "high_school": [], "postal_code": ["45890"]}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)

        self.assertIn(response.status_code, [200,302])

    def test_profile_information_address_has_multiple_suggestions(self):
        my_dict = {"city": ["Baltimore"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MD", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["1 rosedale"],
                   "high_school": [], "postal_code": ["21229"]}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)

        self.assertIn(response.status_code, [200,302])

    def test_profile_information_pleb_does_not_exist(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        self.user.username = "fakeeemail"
        request.user = self.user
        response = profile_information(request)
        # Redirects a non-existent user to the defined login url which at the
        # time of this writing is /registration/signup/confirm/. This is done
        # by the decorator returning False if the user does not exist.
        # This is contrary to throwing a 404.
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_profile_information_complete_profile_info(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        self.pleb.completed_profile_info = True
        self.pleb.save()
        request.user = self.user
        response = profile_information(request)

        self.assertEqual(response.status_code, 302)
        self.pleb.completed_profile_info = False
        self.pleb.save()

    def test_profile_information_underage(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": [datetime.datetime.now()-
                                                    datetime.timedelta(
                                                        days=12*365)],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)

        request.user = self.user
        response = profile_information(request)

        self.assertEqual(response.status_code, 302)

    def test_profile_information_view_already_has_address_valid(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        address = Address(address_hash=str(uuid1())).save()
        self.pleb.address.connect(address)
        request.user = self.user
        response = profile_information(request)

        self.assertEqual(response.status_code, 302)

    def test_profile_information_view_already_has_address_invalid(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"],
                   "valid": "invalid", "original_selected": True,
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        address = Address(address_hash=str(uuid1())).save()
        self.pleb.address.connect(address)
        request.user = self.user
        response = profile_information(request)

        self.assertEqual(response.status_code, 302)

    def test_profile_information_view_invalid_address(self):
        my_dict = {"city": ["Walled Lake"], "home_town": [],
                   "country": ["United States"],
                   "address_additional": [], "employer": [],
                   "state": "MI", "date_of_birth": ["06/04/94"],
                   "college": [], "primary_address": ["125 Glenwood Dr"],
                   "high_school": [], "postal_code": ["48390"],
                   "valid": "invalid", "original_selected": True,
                   "congressional_district": 11, "longitude": -83.4965,
                   "latitude": 42.53202}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)

        self.assertEqual(response.status_code, 302)


class TestSignupView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_anon_user(self):
        self.client.logout()
        response = self.client.get(reverse('signup'))

        self.assertIn(response.status_code, [200, 302])

    def test_logged_in_user(self):
        self.client.login(username=self.user.username, password='testpassword')
        response = self.client.get(reverse('signup'))

        self.assertIn(response.status_code, [200, 302])
        self.client.logout()


class TestSignupAPIView(TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_signup_view_api_success(self):
        signup_dict = {
            'first_name': 'Tyler',
            'last_name': 'Wiersing',
            'email': 'ooto@simulator.amazonses.com',
            'password': 'testpassword',
            'password2': 'testpassword',
            'birthday': "06/23/1990"
        }
        request = self.factory.post('/registration/signup/', data=signup_dict,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s
        res = signup_view_api(request)
        self.assertEqual(res.status_code, 200)

    def test_signup_view_api_failure_user_exists(self):

        signup_dict = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'password': 'testpassword',
            'password2': 'testpassword',
            'birthday': "06/23/1990"
        }

        request = self.factory.post('/registration/signup/', data=signup_dict,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s
        res = signup_view_api(request)
        res.render()
        self.assertEqual(loads(res.content)['detail'],
                         'A user with this email already exists!')
        self.assertEqual(res.status_code, 401)

    def test_signup_view_api_failure_passwords_do_not_match(self):
        signup_dict = {
            'first_name': 'Tyler',
            'last_name': 'Wiersing',
            'email': 'success@simulator.amazonses.com',
            'password': 'testpass',
            'password2': 'not the same as the first',
            'birthday': "06/23/1990"
        }
        request = self.factory.post('/registration/signup/', data=signup_dict,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s
        res = signup_view_api(request)
        res.render()

        self.assertEqual(loads(res.content)['detail'],
                         'Passwords do not match!')
        self.assertEqual(res.status_code, 401)



class TestLoginView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_login_view_success(self):
        request = self.factory.request()
        res = login_view(request)

        self.assertEqual(res.status_code, 200)


class TestLoginAPIView(TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_login_api_view_success(self):
        login_data = {
            'email': self.user.email,
            'password': 'testpassword'
        }

        request = self.factory.post('/registration/login/api/', data=login_data,
                                    format='json')
        s=SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'], 'success')
        self.assertEqual(res.status_code, 200)

    def test_login_api_view_inactive_user(self):
        login_data = {
            'email': self.user.email,
            'password': 'testpassword'
        }
        self.user.is_active = False
        self.user.save()
        request = self.factory.post('/registration/login/api/', data=login_data,
                                    format='json')
        s=SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'], 'account disabled')
        self.assertEqual(res.status_code, 400)

    def test_login_api_view_invalid_password(self):
        login_data = {
            'email': self.user.email,
            'password': 'incorrect password'
        }
        request = self.factory.post('/registration/login/api/', data=login_data,
                                    format='json')
        s=SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'], 'invalid password')
        self.assertEqual(res.status_code, 400)

    def test_login_api_view_user_does_not_exist(self):
        login_data = {
            'email': 'reallydoesntexist@fake.com',
            'password': 'incorrect password'
        }
        request = self.factory.post('/registration/login/api/', data=login_data,
                                    format='json')
        s=SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'], 'cannot find user')
        self.assertEqual(res.status_code, 400)

    def test_login_api_view_incorrect_data_int(self):
        request = self.factory.post('/registration/login/api/', data=1231,
                                    format='json')
        s=SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        self.assertEqual(res.status_code, 400)

    def test_login_api_view_incorrect_data_string(self):
        request = self.factory.post('/registration/login/api/', data='teststring',
                                    format='json')
        s=SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        self.assertEqual(res.status_code, 400)

    def test_login_api_view_incorrect_data_float(self):
        request = self.factory.post('/registration/login/api/', data=1.1234,
                                    format='json')
        s=SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        self.assertEqual(res.status_code, 400)

    def test_login_api_view_incorrect_data_image(self):
        request = self.factory.post('/registration/login/api/', data=1231,
                                    format='json')
        s=SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        self.assertEqual(res.status_code, 400)


class TestLogoutView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_logout_view_success(self):
        user = authenticate(username=self.user.username,
                            password='testpassword')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        res = logout_view(request)

        self.assertEqual(res.status_code, 302)


class TestEmailVerificationView(TestCase):
    def setUp(self):
        self.token_gen = EmailAuthTokenGenerator()
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = False
        self.pleb.save()

    def test_email_verification_view_success(self):
        user = authenticate(username=self.user.username,
                            password='testpassword')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        pleb = Pleb.nodes.get(email=user.email)
        token = self.token_gen.make_token(user, pleb)

        res = email_verification(request, token)

        self.assertEqual(res.status_code, 302)

    def test_email_verification_view_incorrect_token(self):
        user = authenticate(username=self.user.username,
                            password='testpassword')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user

        res = email_verification(request, 'this is a fake token')

        self.assertEqual(res.status_code, 401)

    def test_email_verification_view_pleb_does_not_exist(self):
        user = authenticate(username=self.user.username,
                            password='testpassword')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        request.user.username = "totallyfakeusername"
        token = self.token_gen.make_token(user, None)

        res = email_verification(request, token)
        # This redirects to logout and then subsequently login because we
        # currently don't have an email verification failure page if the
        # user does not exist. See WA-1058
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)


class TestResendEmailVerificationView(TestCase):
    def setUp(self):
        self.token_gen = EmailAuthTokenGenerator()
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = False
        self.pleb.save()

    def test_resend_email_verification_view_success(self):
        user = authenticate(username=self.user.username,
                            password='testpassword')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user

        res = resend_email_verification(request)

        self.assertEqual(res.status_code, 302)

    def test_resend_email_verification_view_failure_pleb_does_not_exist(self):
        user = authenticate(username=self.user.username,
                            password='testpassword')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        request.user.username = 'totallynotafakeuser'
        res = resend_email_verification(request)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class TestConfirmView(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_anon_user(self):
        self.client.logout()
        response = self.client.get(reverse('confirm_view'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user(self):
        self.client.login(username=self.user.username,
                          password='testpassword')
        response = self.client.get(reverse('confirm_view'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.client.logout()


class TestAgeRestrictionView(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_anon_user(self):
        self.client.logout()
        response = self.client.get(reverse('age_restriction_13'), follow=True)

        self.assertEqual(response.status_code, 200)

    def test_logged_in_user(self):
        self.client.login(username=self.user.username, password='testpassword')
        response = self.client.get(reverse('age_restriction_13'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.client.logout()

class TestProfilePictureView(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.save()
'''
    def test_profile_picture_view(self):
        self.client.login(username=self.user.username, password='testpassword')
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            response = self.client.post(reverse('profile_picture'),
                                    data={'picture': image_file})

        self.assertEqual(response.status_code, 302)
'''