import time

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from neomodel.exception import DoesNotExist

from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_registration.utils import create_user_util_test


class SolutionEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.title = "test question title"
        self.question = Question(content="Hey I'm a question",
                                 title=self.title,
                                 owner_username=self.pleb.username).save()
        self.solution = Solution(content="This is a test solution",
                                 owner_username=self.pleb.username).save()
        self.solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(self.solution)
        self.question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(self.question)
        self.user = User.objects.get(email=self.email)
        try:
            Tag.nodes.get(name='taxes')
        except DoesNotExist:
            Tag(name='taxes').save()
        try:
            Tag.nodes.get(name='fiscal')
        except DoesNotExist:
            Tag(name='fiscal').save()
        try:
            Tag.nodes.get(name='environment')
        except DoesNotExist:
            Tag(name='environment').save()

    def test_unauthorized(self):
        url = reverse('solution-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('solution-detail',
                      kwargs={"object_uuid": self.solution.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('solution-detail',
                      kwargs={"object_uuid": self.solution.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('solution-detail',
                      kwargs={"object_uuid": self.solution.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('solution-detail',
                      kwargs={"object_uuid": self.solution.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('solution-detail',
                      kwargs={"object_uuid": self.solution.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("question-solutions",
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "question": self.question.object_uuid,
            "content": self.solution.content
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_html(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("question-solutions",
                      kwargs={'object_uuid': self.question.object_uuid}) \
            + "?html=true"
        data = {
            "question": self.question.object_uuid,
            "content": self.solution.content
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("question-solutions",
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_renderer(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("question-solution-html",
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_solution_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("solution-detail",
                      kwargs={'object_uuid': self.solution.object_uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
