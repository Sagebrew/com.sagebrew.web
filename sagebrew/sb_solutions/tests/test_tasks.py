from uuid import uuid1

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.test import APITestCase

from neomodel import db

from sagebrew.sb_registration.utils import create_user_util_test

from sagebrew.sb_questions.neo_models import Question
from sagebrew.sb_solutions.tasks import create_solution_summary_task


class TestSolutionSummaryTasks(APITestCase):

    def setUp(self):
        settings.DEBUG = True
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content="Hey I'm a question",
                                 title=str(uuid1()),
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)

    def tearDown(self):
        settings.DEBUG = False
        settings.CELERY_ALWAYS_EAGER = False

    def test_summary_solution_does_not_exist(self):
        query = 'MATCH (a:Solution) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        bad_uuid = str(uuid1())
        res = create_solution_summary_task.apply_async(
            kwargs={"object_uuid": bad_uuid})
        self.assertIsInstance(res.result, Exception)

    def test_summary_solution_exists(self):
        content = "My content that needs to be converted into a summary."
        query = 'MATCH (a:Solution) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        url = reverse("question-solutions",
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "question": self.question.object_uuid,
            "content": content
        }
        response = self.client.post(url, data, format='json')
        res = create_solution_summary_task.apply_async(
            kwargs={"object_uuid": response.data['id']})
        self.assertTrue(res.result.summary, content)
