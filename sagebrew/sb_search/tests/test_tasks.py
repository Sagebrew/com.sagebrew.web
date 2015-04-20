import time
import pickle
import pytz
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from elasticsearch import Elasticsearch

from api.utils import wait_util
from plebs.neo_models import Pleb
from api.alchemyapi import AlchemyAPI
from sb_questions.neo_models import Question
from sb_search.tasks import (update_weight_relationship,
                             add_user_to_custom_index, update_user_indices,
                             update_search_query, create_keyword)
from sb_registration.utils import create_user_util_test


class TestUpdateWeightRelationshipTaskQuestion(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(object_uuid=str(uuid1()))
        self.question.save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_weight_relationship_task_success_seen_unconnected(self):
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'search_seen'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_comment_on_unconnected(
            self):
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'comment_on'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 150)

    def test_update_weight_relate_task_success_inappropriate_unconnect(self):
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'flag_as_inappropriate'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_spam_unconnected(
            self):
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'flag_as_spam'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_share_unconnected(self):
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'share'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_solutioned_unconnected(
            self):
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'solution'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)

    def test_update_weight_relationship_task_success_seen_connected(self):
        res = self.pleb.object_weight.connect(self.question)
        res.save()

        self.assertIsNot(res, False)

        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'seen_search'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 155)

    def test_update_weight_relationship_task_success_comment_on_connected(self):
        res = self.pleb.object_weight.connect(self.question)
        res.save()
        self.assertIsNot(res, False)

        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'comment_on'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 155)

    def test_update_weight_relate_task_success_flag_as_inappropriate_connected(
            self):
        res = self.pleb.object_weight.connect(self.question)
        res.save()
        self.assertIsNot(res, False)

        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'flag_as_inappropriate'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 145)

    def test_update_weight_relationship_task_success_flag_as_spam_connected(
            self):
        res = self.pleb.object_weight.connect(self.question)
        res.save()
        self.assertIsNot(res, False)

        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'flag_as_spam'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 50)

    def test_update_weight_relationship_task_success_share_connected(self):
        res = self.pleb.object_weight.connect(self.question)
        res.save()
        self.assertIsNot(res, False)

        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'share'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 157)

    def test_update_weight_relationship_task_success_solutioned_connected(self):
        res = self.pleb.object_weight.connect(self.question)
        res.save()
        self.assertIsNot(res, False)

        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': self.user.email,
            'modifier_type': 'solution'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.object_weight.is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(
            self.pleb.object_weight.relationship(self.question).weight, 200)

    def test_update_weight_relationship_task_pleb_does_not_exist(self):
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'question',
            'object_uuid': self.question.object_uuid,
            'current_pleb': str(uuid1()),
            'modifier_type': 'solution'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

    def test_update_weight_relationship_task_question_does_not_exist(self):
        pass


class TestUpdateWeightRelationshipTaskPleb(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_weight_relationship_task_success_seen_unconnected(self):
        pleb2 = Pleb(email=str(uuid1())).save()
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'pleb',
            'object_uuid': self.pleb.email,
            'current_pleb': pleb2.email,
            'modifier_type': 'search_seen'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        pleb2.refresh()

        self.assertTrue(pleb2.user_weight.is_connected(self.pleb))
        self.assertTrue(res)

        self.assertEqual(
            pleb2.user_weight.relationship(self.pleb).weight, 150)

    def test_update_weight_relationship_task_success_seen_connected(self):
        pleb2 = Pleb(email=str(uuid1())).save()
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'pleb',
            'object_uuid': self.pleb.email,
            'current_pleb': pleb2.email,
            'modifier_type': 'search_seen'
        }
        rel = pleb2.user_weight.connect(self.pleb)
        rel.save()
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        pleb2.refresh()

        self.assertTrue(pleb2.user_weight.is_connected(self.pleb))
        self.assertTrue(res)

        self.assertEqual(
            pleb2.user_weight.relationship(self.pleb).weight, 160)

    def test_update_weight_relationship_task_failure_pleb_does_not_exist(self):
        data = {
            "document_id": str(uuid1()),
            'index': 'full-search-user-specific-1',
            'object_type': 'pleb',
            'object_uuid': self.pleb.email,
            'current_pleb': str(uuid1()),
            'modifier_type': 'search_seen'
        }
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)


class TestAddUserToCustomIndexTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
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
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_user_indices_success(self):
        search_dict = {
            'question_content': 'test_c', 'user': self.user.email,
            'title': 'test_t', 'tags': ['test', 'tag'],
            'object_uuid': str(uuid1()),
            'post_date': datetime.now(pytz.utc),
            'related_user': ''
        }
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
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
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

        test_query = SearchQuery(search_query=str(uuid1()))
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

    def test_update_search_query_success_pleb_does_not_exist(self):
        from sb_search.neo_models import SearchQuery

        test_query = SearchQuery(search_query="this is a test search query")
        test_query.save()

        task_data = {
            "pleb": str(uuid1()), "query_param": test_query.search_query,
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertIsInstance(res, Exception)

    def test_update_search_query_success_pleb_does_not_exist_pickle(self):
        from sb_search.neo_models import SearchQuery

        test_query = SearchQuery(search_query=str(uuid1()))
        test_query.save()

        task_data = {
            "pleb": str(uuid1()), "query_param": test_query.search_query,
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        res = res.result
        pickle_instance = pickle.dumps(res)
        self.assertTrue(pickle_instance)
        self.assertIsInstance(pickle.loads(pickle_instance), Exception)


class TestCreateKeywordTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
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

        query = SearchQuery(search_query="test_query")
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

    def test_create_keyword_task_failure_search_query_does_not_exist(self):
        from sb_search.neo_models import KeyWord

        keyword = KeyWord(keyword="test")
        keyword.save()

        data = {
            "text": "test", "relevance": ".9",
            "query_param": str(uuid1())
        }

        res = create_keyword.apply_async(kwargs=data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)
