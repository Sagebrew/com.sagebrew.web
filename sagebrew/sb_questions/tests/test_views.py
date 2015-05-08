from uuid import uuid1

from django.contrib.auth.models import User

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
                            title='test title').save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/search/%s/' %
                              question.object_uuid)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
