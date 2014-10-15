import time
import pytz
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command

from elasticsearch import Elasticsearch

from plebs.neo_models import Pleb
from api.alchemyapi import AlchemyAPI
from sb_posts.neo_models import SBPost
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion
from sb_search.tasks import (update_weight_relationship,
                             add_user_to_custom_index, update_user_indices,
                             update_search_query, create_keyword)

class TestUpdateWeightRelationshipTaskQuestion(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.question = SBQuestion(question_id=str(uuid1()))
        self.question.save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False
        call_command('clear_neo_db')

    def test_update_weight_relationship_task_success_seen_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'search_seen'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_comment_on_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'comment_on'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_inappropriate_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_inappropriate'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_spam_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_spam'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_share_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'share'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_answered_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'answered'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

    def test_update_weight_relationship_task_success_seen_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'search_seen'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 155)

    def test_update_weight_relationship_task_success_comment_on_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'comment_on'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 155)

    def test_update_weight_relationship_task_success_flag_as_inappropriate_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_inappropriate'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 145)

    def test_update_weight_relationship_task_success_flag_as_spam_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_spam'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 50)

    def test_update_weight_relationship_task_success_share_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'share'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 157)

    def test_update_weight_relationship_task_success_answered_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'answered'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 200)

class TestUpdateWeightRelationshipTaskAnswer(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.answer = SBAnswer(answer_id=str(uuid1()))
        self.answer.save()

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_weight_relationship_task_success_seen_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'search_seen'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_comment_on_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'comment_on'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_inappropriate_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_inappropriate'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_spam_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_spam'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_share_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'share'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_seen_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'search_seen'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 155)

    def test_update_weight_relationship_task_success_comment_on_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'comment_on'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 155)

    def test_update_weight_relationship_task_success_flag_as_inappropriate_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_inappropriate'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 145)

    def test_update_weight_relationship_task_success_flag_as_spam_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_spam'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 50)

    def test_update_weight_relationship_task_success_share_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'share'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 157)

class TestUpdateWeightRelationshipTaskPleb(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb1 = Pleb.nodes.get(email=self.user1.email)

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

class TestUpdateWeightRelationshipTaskPost(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb1 = Pleb.nodes.get(email=self.user1.email)
        self.user2 = User.objects.create_user(
            username='Tyler2', email=str(uuid1())+'@gmail.com')
        self.pleb2 = Pleb.nodes.get(email=self.user2.email)

    def tearDown(self):
        call_command('clear_neo_db')

class TestAddUserToCustomIndexTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_user_to_custom_index_success(self):
        data = {
            'pleb': self.user.email
        }
        res = add_user_to_custom_index.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)


class TestUpdateUserIndices(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_user_indices_success(self):
        search_dict = {'question_content': 'test_c', 'user': self.user.email,
                       'question_title': 'test_t', 'tags': ['test','tag'],
                       'question_uuid': str(uuid1()),
                       'post_date': datetime.now(pytz.utc),
                       'related_user': ''}
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res = es.index(index='full-search-base', doc_type='question',
                       body=search_dict)
        task_data = {
            "doc_id": res['_id'],
            "doc_type": res['_type']
        }

        res = update_user_indices.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)


class TestUpdateSearchQuery(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_search_query_success_search_query_does_not_exist(self):
        from sb_search.neo_models import SearchQuery
        query_param = "this is a test search thing"
        alchemyapi = AlchemyAPI()
        response = alchemyapi.keywords("text", query_param)
        task_data = {
            "pleb": self.pleb.email, "query_param": query_param,
            "keywords": response['keywords']
        }
        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

        test_query = SearchQuery.nodes.get(search_query=query_param)
        rel = self.pleb.searches.relationship(test_query)

        self.assertEqual(test_query.__class__, SearchQuery)
        self.assertEqual(rel.times_searched, 1)

    def test_update_search_query_success_search_query_exists_connected(self):
        from sb_search.neo_models import SearchQuery
        test_query = SearchQuery(search_query="this is a test search")
        test_query.save()

        rel = self.pleb.searches.connect(test_query)
        rel.save()

        task_data = {
            "pleb": self.pleb.email, "query_param": test_query.search_query,
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

        test_query.refresh()

        rel = self.pleb.searches.relationship(test_query)

        self.assertEqual(rel.times_searched, 2)

    def test_update_search_query_success_search_query_exists_unconnected(self):
        from sb_search.neo_models import SearchQuery
        test_query = SearchQuery(search_query="this is a test search")
        test_query.save()

        task_data = {
            "pleb": self.pleb.email, "query_param": test_query.search_query,
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

        test_query.refresh()

        rel = self.pleb.searches.relationship(test_query)

        self.assertEqual(rel.times_searched, 1)


class TestCreateKeywordTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_keyword_task_success_keyword_does_not_exist(self):
        from sb_search.neo_models import SearchQuery
        query = SearchQuery(search_query="test query")
        query.save()

        data = {
            "text": "test", "relevance": ".9",
            "query_param": query.search_query
        }

        res = create_keyword.apply_async(kwargs=data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_create_keyword_task_success_keyword_exists(self):
        from sb_search.neo_models import SearchQuery, KeyWord
        query = SearchQuery(search_query="test query")
        query.save()
        keyword = KeyWord(keyword="test")
        keyword.save()

        data = {
            "text": "test", "relevance": ".9",
            "query_param": query.search_query
        }

        res = create_keyword.apply_async(kwargs=data, )

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

'''
    def test_create_keyword_task_failure_search_query_does_not_exist(self):
        from sb_search.neo_models import SearchQuery, KeyWord
        keyword = KeyWord(keyword="test")
        keyword.save()

        data = {
            "text": "test", "relevance": ".9",
            "query_param": "this does not exist"
        }

        res = create_keyword.apply_async(kwargs=data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)
'''