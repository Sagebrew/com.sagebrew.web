import shortuuid
from uuid import uuid1
from json import loads
from base64 import b64encode

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import call_command
from rest_framework.test import APIRequestFactory, APIClient

from sb_registration.views import (profile_information, confirm_view,
                                   signup_view_api, signup_view, logout_view,
                                   login_view, login_view_api,
                                   resend_email_verification,
                                   email_verification)
from plebs.neo_models import Pleb


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


class ProfileInfoTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def tearDown(self):
        call_command('clear_neo_db')

    def test_user_info_population_no_birthday(self):
        my_dict = {'date_of_birth': [u'']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_user_info_population_incorrect_birthday(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_zipcode(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_primary(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u''],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertEqual(response.status_code, 200)

    def test_address_validation_util_invalid_no_country(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u''], u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])

    def test_address_validation_util_invalid_no_city(self):
        my_dict = {u'city': [u''], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertEqual(response.status_code, 200)

    def test_address_validation_util_valid(self):
        my_dict = {u'city': [u'Walled Lake'], u'home_town': [u''],
                   u'country': [u'United States'],
                   u'address_additional': [u''],
                   u'employer': [u''], u'state': [u'Mi'],
                   u'date_of_birth': [u'06/04/94'], u'college': [u''],
                   u'primary_address': [u'125 Glenwood Dr.'],
                   u'csrfmiddlewaretoken': [
                       u'GjnOBap0nEwKUgQ9fZbQMKZL8HkO5kIt'],
                   u'high_school': [u''], u'postal_code': [u'48390']}
        request = self.factory.post('/registration/profile_information',
                                    data=my_dict)
        request.user = self.user
        response = profile_information(request)
        self.assertIn(response.status_code, [200,302])


class TestSignupView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def tearDown(self):
        call_command('clear_neo_db')

    def test_signup_view(self):
        request = self.factory.request()
        res = signup_view(request)

        self.assertEqual(res.status_code, 200)

class TestSignupAPIView(TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def tearDown(self):
        call_command('clear_neo_db')

    def test_signup_view_api_success(self):
        signup_dict = {
            'first_name': 'Tyler',
            'last_name': 'Wiersing',
            'email': 'success@simulator.amazonses.com',
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
        user = User.objects.create_user(first_name='Tyler',
                                        last_name='Wiersing',
                                        email='success@simulator.amazonses.com',
                                        username=shortuuid.uuid(),
                                        password='testpass')
        user.save()

        signup_dict = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
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
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def tearDown(self):
        call_command('clear_neo_db')

    def test_login_view_success(self):
        request = self.factory.request()
        res = login_view(request)

        self.assertEqual(res.status_code, 200)

class TestLoginAPIView(TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com',
            password='testpass')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def tearDown(self):
        call_command('clear_neo_db')

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
