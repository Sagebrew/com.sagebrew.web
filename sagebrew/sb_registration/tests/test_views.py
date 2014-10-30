import shortuuid
from json import loads
from base64 import b64encode

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.test import APIRequestFactory

from api.utils import test_wait_util
from sb_registration.views import (profile_information, confirm_view,
                                   signup_view_api, signup_view, logout_view,
                                   login_view, login_view_api,
                                   resend_email_verification,
                                   email_verification,)
from sb_registration.models import EmailAuthTokenGenerator
from sb_registration.utils import create_user_util
from plebs.neo_models import Pleb, Address


class InterestsTest(TestCase):
    def setup(self):
        self.user = User.objects.get(pk=2)

    def test_no_categories_no_topics_selected(self):
        pass

    def test_all_categories_no_topics_selected(self):
        pass

    def test_all_topics_no_cat_selected(self):
        pass

    def test_all_categories_all_topics_selected(self):
        pass

    def test_random_cat_selected_no_topics_selected(self):
        pass

    def test_random_cat_selected_random_topics_selected(self):
        pass

    def test_no_cat_selected_random_topics_selected(self):
        pass

    def test_get_request(self):
        pass


class TestProfileInfoView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()
        addresses = Address.nodes.all()
        for address in addresses:
            if address.address.is_connected(self.pleb):
                address.address.disconnect(self.pleb)
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
                   "high_school": [], "postal_code": ["48390"], "valid": "valid",
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

        self.assertIn(response.status_code, [200,302])

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

class TestSignupView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_signup_view(self):
        request = self.factory.request()
        res = signup_view(request)

        self.assertEqual(res.status_code, 200)

class TestSignupAPIView(TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("Tyler", "Wiersing", self.email, "testpassword",
                               username=shortuuid.uuid())
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_signup_view_api_success(self):
        signup_dict = {
            'first_name': 'Tyler',
            'last_name': 'Wiersing',
            'email': 'ooto@simulator.amazonses.com',
            'password': 'testpass',
            'password2': 'testpass'
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
            'password': 'testpass',
            'password2': 'testpass'
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
            'password2': 'not the same as the first'
        }
        request = self.factory.post('/registration/signup/', data=signup_dict,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s
        res = signup_view_api(request)
        res.render()

        self.assertEqual(loads(res.content)['detail'], 'Passwords do not match!')
        self.assertEqual(res.status_code, 401)

    def test_signup_view_api_failure_incorrect_data_type_int(self):
        request = self.factory.post('/registration/signup/', data=10010101010,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s
        res = signup_view_api(request)
        res.render()

        self.assertEqual(res.status_code, 400)

    def test_signup_view_api_failure_incorrect_data_type_float(self):
        request = self.factory.post('/registration/signup/', data=1.1010,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s
        res = signup_view_api(request)
        res.render()

        self.assertEqual(res.status_code, 400)

    def test_signup_view_api_failure_incorrect_data_type_image(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/registration/signup/', data=image,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s
        res = signup_view_api(request)
        res.render()

        self.assertEqual(res.status_code, 400)

    def test_signup_view_api_failure_incorrect_data_type_string(self):
        request = self.factory.post('/registration/signup/', data='teststring',
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s
        res = signup_view_api(request)
        res.render()

        self.assertEqual(res.status_code, 400)

class TestLoginView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
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
        res = create_user_util("test", "test", self.email, "testpass")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_login_api_view_success(self):
        login_data = {
            'email': self.user.email,
            'password': 'testpass'
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
            'password': 'testpass'
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
        res = create_user_util("test", "test", self.email, "testpass")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_logout_view_success(self):
        user = authenticate(username=self.user.username,
                            password='testpass')
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
        res = create_user_util("test", "test", self.email, "testpass")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = False
        self.pleb.save()

    def test_email_verification_view_success(self):
        user = authenticate(username=self.user.username,
                            password='testpass')
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
                            password='testpass')
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
                            password='testpass')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        request.user.email = "totallynotafakeuser@fake.com"
        token = self.token_gen.make_token(user, None)

        res = email_verification(request, token)

        self.assertEqual(res.status_code, 302)

class TestResendEmailVerificationView(TestCase):
    def setUp(self):
        self.token_gen = EmailAuthTokenGenerator()
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpass")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = False
        self.pleb.save()

    def test_resend_email_verification_view_success(self):
        user = authenticate(username=self.user.username,
                            password='testpass')
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
                            password='testpass')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        request.user.email = 'totallynotafakeuser@fake.com'
        res = resend_email_verification(request)

        self.assertEqual(res.status_code, 400)



