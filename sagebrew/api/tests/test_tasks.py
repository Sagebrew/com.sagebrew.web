import time
from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_registration.utils import create_user_util_test
from api.tasks import add_object_to_search_index


class TestAddObjectToSearchIndex(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertFalse(isinstance(res, Exception))
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(object_uuid=str(uuid1()))
        self.question.save()
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_object_to_search_index(self):
        task_data = {
            'object_uuid': self.question.object_uuid,
            'object_data': QuestionSerializerNeo(self.question).data
        }

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_add_object_to_search_index_pleb_already_populated(self):
        task_data = {
            'object_uuid': self.pleb.object_uuid,
            'object_data': QuestionSerializerNeo(self.question).data
        }
        self.pleb.populated_es_index = True
        self.pleb.save()

        res = add_object_to_search_index.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.pleb.populated_es_index = False
        self.pleb.save()
