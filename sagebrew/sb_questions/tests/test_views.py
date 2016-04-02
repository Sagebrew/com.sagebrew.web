from uuid import uuid1

from django.contrib.auth.models import User
from django.core.cache import cache
from django.template.response import TemplateResponse

from neomodel import db

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_questions.neo_models import Question


class TestGetQuestionSearchView(APITestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()

    def test_get_question_search_view_success(self):
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/search/%s/' %
                              question.object_uuid)
        self.assertTrue(res.status_code, status.HTTP_200_OK)


class TestGetQuestionView(APITestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()

    def test_get_question_view_success(self):
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/%s/' %
                              question.object_uuid)
        self.assertTrue(res.status_code, status.HTTP_200_OK)


class TestGetQuestionListView(APITestCase):

    def setUp(self):
        cache.clear()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()

    def test_get_question_list_view_success(self):
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/')
        self.assertTrue(res.status_code, status.HTTP_200_OK)

    def test_get_question_list_view_html_snapshot_single_success(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        res = self.client.get('/conversations/?_escaped_fragment_=')
        self.assertTrue(res.status_code, status.HTTP_200_OK)


class TestSingleQuestionPage(APITestCase):

    def setUp(self):
        cache.clear()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()
        self.question = Question(title=str(uuid1()),
                                 content="some test content").save()

    def test_get_single_page(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("single_question_page",
                      kwargs={"object_uuid": self.question.object_uuid})
        res = self.client.get(url, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res, TemplateResponse)
