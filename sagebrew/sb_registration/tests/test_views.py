#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import loads

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import login, authenticate
from django.test import TestCase, RequestFactory, Client
from django.contrib.sessions.backends.db import SessionStore
from django.core.urlresolvers import reverse
from django.core.cache import cache

from rest_framework.test import APIRequestFactory
from rest_framework import status

from neomodel import db

from sb_registration.views import (logout_view,
                                   login_view, login_view_api,
                                   email_verification,
                                   advocacy, political_campaign,
                                   quest_signup, signup_view)
from plebs.serializers import EmailAuthTokenGenerator
from sb_registration.utils import create_user_util_test
from plebs.neo_models import Pleb


class TestSignupView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_anon_user(self):
        self.client.logout()
        response = self.client.get(reverse('signup'))

        self.assertIn(response.status_code, [status.HTTP_200_OK,
                                             status.HTTP_302_FOUND])

    def test_logged_in_user(self):
        self.client.login(username=self.user.username, password='test_test')
        response = self.client.get(reverse('signup'))

        self.assertIn(response.status_code, [status.HTTP_200_OK,
                                             status.HTTP_302_FOUND])
        self.client.logout()

    def test_signup_email_verified(self):
        user = authenticate(username=self.user.username,
                            password='test_test')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        self.pleb.completed_profile_info = False
        self.pleb.email_verified = True
        self.pleb.save()
        res = signup_view(request)
        self.assertIn(res.status_code, [status.HTTP_200_OK,
                                        status.HTTP_302_FOUND])
        self.pleb.email_verified = False
        self.pleb.save()

    def test_signup_profile_does_not_exist(self):
        query = 'MATCH (a) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        user = authenticate(username=self.user.username,
                            password='test_test')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        self.pleb.email_verified = True
        self.pleb.save()
        res = signup_view(request)
        self.assertIn(res.status_code, [status.HTTP_200_OK,
                                        status.HTTP_302_FOUND])
        self.pleb.email_verified = False
        self.pleb.save()

    def test_signup_completed_profile(self):
        user = authenticate(username=self.user.username,
                            password='test_test')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        self.pleb.email_verified = True
        self.pleb.save()
        res = signup_view(request)
        self.assertIn(res.status_code, [status.HTTP_200_OK,
                                        status.HTTP_302_FOUND])
        self.pleb.email_verified = False
        self.pleb.save()


class TestLoginView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_login_view_success(self):
        request = self.factory.request()
        res = login_view(request)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_view_authed(self):
        self.client.login(username=self.user.username, password='test_test')
        request = self.factory.request()
        request.user = self.user
        res = login_view(request)

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.client.logout()


class TestFeatureViews(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_advocacy_view_success(self):
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        request.user = AnonymousUser()
        res = advocacy(request)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_advocacy_logged_in(self):
        user = authenticate(username=self.user.username,
                            password='test_test')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        res = advocacy(request)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_political_campaign_view_success(self):
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        request.user = AnonymousUser()
        res = political_campaign(request)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_political_campaign_view_no_positions(self):
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        request.user = AnonymousUser()
        query = 'MATCH (a:Position) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        res = political_campaign(request)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_political_campaign_logged_in(self):
        user = authenticate(username=self.user.username,
                            password='test_test')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        res = political_campaign(request)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)


class TestLoginAPIView(TestCase):

    def setUp(self):
        self.store = SessionStore()
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_login_api_view_success(self):
        login_data = {
            'email': self.user.email,
            'password': 'test_test'
        }

        request = self.factory.post('/registration/login/api/', data=login_data,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'], 'success')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_api_view_inactive_user(self):
        login_data = {
            'email': self.user.email,
            'password': 'test_test'
        }
        self.user.is_active = False
        self.user.save()
        request = self.factory.post('/registration/login/api/', data=login_data,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'],
                         'This account has been disabled.')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api_view_invalid_password(self):
        login_data = {
            'email': self.user.email,
            'password': 'incorrect password'
        }
        request = self.factory.post('/registration/login/api/', data=login_data,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'],
                         'Incorrect password and username combination.')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api_view_user_does_not_exist(self):
        login_data = {
            'email': 'reallydoesntexist@fake.com',
            'password': 'incorrect password'
        }
        request = self.factory.post('/registration/login/api/', data=login_data,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'],
                         'Incorrect password and username combination.')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api_view_incorrect_data_int(self):
        request = self.factory.post('/registration/login/api/', data=1231,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api_view_incorrect_data_string(self):
        request = self.factory.post('/registration/login/api/',
                                    data='teststring',
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api_view_incorrect_data_float(self):
        request = self.factory.post('/registration/login/api/', data=1.1234,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api_view_incorrect_data_image(self):
        request = self.factory.post('/registration/login/api/', data=1231,
                                    format='json')
        s = SessionStore()
        s.save()
        request.session = s

        res = login_view_api(request)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestLogoutView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()

    def test_logout_view_success(self):
        user = authenticate(username=self.user.username,
                            password='test_test')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        res = logout_view(request)

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)


class TestEmailVerificationView(TestCase):

    def setUp(self):
        self.token_gen = EmailAuthTokenGenerator()
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = False
        self.pleb.save()

    def test_email_verification_view_success(self):
        cache.clear()
        user = authenticate(username=self.user.username,
                            password='test_test')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user
        pleb = Pleb.nodes.get(email=user.email)
        token = self.token_gen.make_token(user, pleb)

        res = email_verification(request, token)

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_email_verification_view_incorrect_token(self):
        user = authenticate(username=self.user.username,
                            password='test_test')
        request = self.factory.request()
        s = SessionStore()
        s.save()
        request.session = s
        login(request, user)
        request.user = user

        res = email_verification(request, 'this is a fake token')

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_email_verification_view_pleb_does_not_exist(self):
        user = authenticate(username=self.user.username,
                            password='test_test')
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


class TestConfirmView(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def test_anon_user(self):
        self.client.logout()
        response = self.client.get(reverse('confirm_view'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_logged_in_user(self):
        self.client.login(username=self.user.username,
                          password='test_test')
        response = self.client.get(reverse('confirm_view'), follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()


class TestAgeRestrictionView(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def test_anon_user(self):
        self.client.logout()
        response = self.client.get(reverse('age_restriction_13'), follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user(self):
        self.client.login(username=self.user.username, password='test_test')
        response = self.client.get(reverse('age_restriction_13'), follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()


class TestQuestSignup(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        self.factory = RequestFactory()
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.user.username = self.pleb.username
        self.user.save()
        self.client.login(username=self.pleb.username, password='test_test')

    def test_quest_signup_get(self):
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = AnonymousUser()
        response = quest_signup(request)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_quest_signup_existing_user(self):
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        response = quest_signup(request)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)


class TestProfilePicture(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()
        cache.set(self.pleb.username, self.pleb)

    def test_profile_picture(self):
        self.client.login(username=self.user.username, password='test_test')
        url = reverse("profile_picture")
        res = self.client.get(url)

        self.assertIn(res.status_code, [status.HTTP_200_OK,
                                        status.HTTP_302_FOUND])
