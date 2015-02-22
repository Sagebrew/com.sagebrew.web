import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from elasticsearch import Elasticsearch

from api.utils import wait_util
from sb_questions.tasks import (create_question_task,
                                add_question_to_indices_task,
                                add_tags_to_question_task)
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util_test


class TestSaveQuestionTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'tags': "this,is,a,test",
                                   'question_uuid': str(uuid1())}

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_save_question_task(self):
        response = create_question_task.apply_async(
            kwargs=self.question_info_dict)
        while not response.ready():
            time.sleep(1)

        self.assertTrue(response.result)

    def test_create_question_task_tags_is_none(self):
        self.question_info_dict['tags'] = None
        response = create_question_task.apply_async(
            kwargs=self.question_info_dict)
        while not response.ready():
            time.sleep(1)

        self.assertTrue(response.result)

    def test_save_question_task_question_exists(self):
        question = SBQuestion(sb_id=str(uuid1()))
        question.save()

        self.question_info_dict['question_uuid'] = question.sb_id

        res = create_question_task.apply_async(kwargs=self.question_info_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)


class TestAddQuestionToIndicesTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = SBQuestion(content="fake content",
                                   question_title="fake title",
                                   sb_id=str(uuid1())).save()
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
                 doc_type='sb_questions.neo_models.SBQuestion',
                 id=self.question.sb_id,
                 body={'content': self.question.content})
        task_data = {
            'question': self.question,
            'tags': ['fake', 'tags']
        }
        res = add_question_to_indices_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)



class TestAddTagsToQuestionTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = SBQuestion(content="fake content",
                                   question_title="fake title",
                                   sb_id=str(uuid1())).save()
        self.question.owned_by.connect(self.pleb)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_tags_to_question_task(self):
        task_data = {
            'question': self.question,
            'tags': 'fake,tags'
        }
        res = add_tags_to_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))

    def test_add_tags_to_question_tags_added(self):
        self.question.tags_added = True
        self.question.save()
        task_data = {
            'question': self.question,
            'tags': 'fake,tags'
        }
        res = add_tags_to_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))


class TestMultipleTasks(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def test_create_many_questions(self):
        response_array = []
        for num in range(1, 10):
            uuid = str(uuid1())
            self.question_info_dict['question_uuid'] = uuid
            save_response = create_question_task.apply_async(
                kwargs=self.question_info_dict)
            while not save_response.ready():
                time.sleep(1)
            response_array.append(save_response.result)

        self.assertNotIn(False, response_array)

    def test_create_same_question_twice(self):
        question = SBQuestion(content="test question", question_title="title",
                              sb_id=str(uuid1()))
        question.save()
        post_info_dict = {'current_pleb': self.pleb.email,
                          'question_title': 'Question Title',
                          'content': 'test question',
                          'question_uuid': question.sb_id,}
        response2 = create_question_task.apply_async(kwargs=post_info_dict)
        same_question = wait_util({"task_id": response2})
        self.assertTrue(same_question)
