from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test


class HelpGoodQuestionTests(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_good_question_helper(self):
        response = self.client.get(reverse('good_question'), follow=True)
        self.assertEqual(response.status_code, 200)


class TestHelpArea(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_help_area(self):
        url = reverse("help_center")
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)


class TestRelatedArticles(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_related_articles(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("related_articles")
        response = self.client.get(url, {'category': 'account',
                                         'current_article':
                                             '/help/accounts/delete_account/'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
