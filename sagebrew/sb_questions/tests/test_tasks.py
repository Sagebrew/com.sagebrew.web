import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from elasticsearch import Elasticsearch

from api.utils import wait_util
from sb_questions.tasks import (add_question_to_indices_task)
from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test


class TestAddQuestionToIndicesTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content="fake content",
                                   title="fake title",
                                   object_uuid=str(uuid1())).save()
        self.question.owned_by.connect(self.pleb)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_question_to_indices_task(self):
        task_data = {
            'question': self.question,
            'tags': ['fake', 'tags']
        }
        res = add_question_to_indices_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))

    def test_add_question_to_indices_task_added_already(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.index(index='full-search-base',
                 doc_type='sb_questions.neo_models.Question',
                 id=self.question.object_uuid,
                 body={'content': self.question.content})
        task_data = {
            'question': self.question,
            'tags': ['fake', 'tags']
        }
        res = add_question_to_indices_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
