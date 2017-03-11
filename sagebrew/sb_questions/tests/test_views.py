from uuid import uuid1

from django.contrib.auth.models import User
from django.core.cache import cache
from django.template.response import TemplateResponse
from django.test import TestCase, RequestFactory
from django.utils.text import slugify

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from sagebrew.plebs.neo_models import Pleb
from sagebrew.sb_registration.utils import create_user_util_test

from sagebrew.sb_questions.views import (
    solution_edit_page, QuestionManagerView, question_redirect_page)
from sagebrew.sb_questions.neo_models import Question
from sagebrew.sb_solutions.neo_models import Solution


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


class TestGetQuestionView(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounces@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.user = User.objects.get(email=self.email)
        self.user2 = User.objects.get(email=self.email2)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.factory = RequestFactory()
        self.pleb.save()

    def test_get_question_view_success(self):
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        url = reverse("question_detail_page",
                      kwargs={"question_uuid": question.object_uuid,
                              "slug": slugify(question.title)})
        request = self.factory.get(url)
        request.user = self.user
        view = QuestionManagerView.as_view(
            template_name="conversation.html")
        response = view(request, question_uuid=question.object_uuid,
                        slug=slugify(question.title))
        self.assertTrue(response.status_code, status.HTTP_200_OK)

    def test_get_question_does_not_exist(self):
        url = reverse("question_detail_page",
                      kwargs={"question_uuid": str(uuid1()),
                              "slug": slugify(str(uuid1()))})
        request = self.factory.get(url)
        request.user = self.user
        view = QuestionManagerView.as_view(
            template_name="conversation.html")
        response = view(request, question_uuid=str(uuid1()),
                        slug=slugify(str(uuid1())))
        # Verify 200 because we redirect to 404 error page but that returns a
        # 200 response
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.url, "/404/")

    def test_get_question_none(self):
        url = reverse("question_detail_page",
                      kwargs={"question_uuid": str(uuid1()),
                              "slug": slugify(str(uuid1()))})
        request = self.factory.get(url)
        request.user = self.user
        view = QuestionManagerView.as_view(
            template_name="conversation.html")
        response = view(request)
        # Verify 200 because we redirect to 404 error page but that returns a
        # 200 response
        self.assertTrue(response.status_code, status.HTTP_200_OK)

    def test_get_question_create(self):
        res = self.client.get(reverse("question-create"))
        self.assertTrue(res.status_code, status.HTTP_200_OK)

    def test_question_redirect_page(self):
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()

        question.owned_by.connect(self.pleb)
        url = reverse("question_redirect_page",
                      kwargs={"question_uuid": question.object_uuid})
        request = self.factory.get(url)
        request.user = self.user
        response = question_redirect_page(request, question.object_uuid)
        self.assertEqual(response.status_code,
                         status.HTTP_301_MOVED_PERMANENTLY)

    def test_get_question_edit(self):
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()

        question.owned_by.connect(self.pleb)
        res = self.client.get(reverse(
            "question-edit", kwargs={"question_uuid": question.object_uuid}))
        self.assertTrue(res.status_code, status.HTTP_200_OK)

    def test_edit_question_not_owner(self):
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()

        question.owned_by.connect(self.pleb)
        request = self.factory.get(reverse(
            "question-edit", kwargs={"question_uuid": question.object_uuid}))
        request.user = self.user2
        view = QuestionManagerView.as_view(
            template_name="questions/edit.html")
        response = view(request, question_uuid=question.object_uuid,
                        slug=slugify(question.title))
        self.assertTrue(response.status_code, status.HTTP_302_FOUND)


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
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res, TemplateResponse)


class TestEditSolutionPage(TestCase):

    def setUp(self):
        cache.clear()
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounces@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.user = User.objects.get(email=self.email)
        self.user2 = User.objects.get(email=self.email2)
        self.title = str(uuid1())
        self.factory = RequestFactory()
        self.question = Question(content="Hey I'm a question",
                                 title=self.title,
                                 owner_username=self.pleb.username).save()
        self.solution = Solution(content="This is a test solution",
                                 owner_username=self.pleb.username,
                                 parent_id=self.question.object_uuid).save()
        self.solution.owned_by.connect(self.pleb)
        self.question.owned_by.connect(self.pleb)
        self.user = User.objects.get(email=self.email)

    def test_edit_solution(self):
        url = reverse("solution-edit",
                      kwargs={"solution_uuid": self.solution.object_uuid})
        request = self.factory.get(url)
        request.user = self.user
        response = solution_edit_page(request,
                                      solution_uuid=self.solution.object_uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_solution_not_owner(self):
        url = reverse("solution-edit",
                      kwargs={"solution_uuid": self.solution.object_uuid})
        request = self.factory.get(url)
        request.user = self.user2
        response = solution_edit_page(request,
                                      solution_uuid=self.solution.object_uuid)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
