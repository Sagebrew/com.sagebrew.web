import time
import pickle
from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from plebs.neo_models import Pleb

from sb_search.tasks import (update_search_query, create_keyword)
from sb_registration.utils import create_user_util_test


class TestUpdateSearchQuery(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_search_query_success_pleb_does_not_exist(self):
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

    def test_update_search_query_success(self):
        from sb_search.neo_models import SearchQuery

        test_query = SearchQuery(search_query=str(uuid1()))
        test_query.save()

        task_data = {
            "pleb": self.pleb.username, "query_param": test_query.search_query,
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_update_search_query_success_already_connected(self):
        from sb_search.neo_models import SearchQuery

        test_query = SearchQuery(search_query=str(uuid1()))
        test_query.save()
        self.pleb.searches.connect(test_query)

        task_data = {
            "pleb": self.pleb.username, "query_param": test_query.search_query,
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_update_search_query_query_does_not_exist(self):
        task_data = {
            "pleb": self.pleb.username, "query_param": str(uuid1()),
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)


class TestCreateKeywordTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_keyword_task_success_keyword_does_not_exist(self):
        from sb_search.neo_models import SearchQuery

        query = SearchQuery(search_query=str(uuid1()))
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
        query.delete()

    def test_create_keyword_task_success_keyword_exists(self):
        from sb_search.neo_models import SearchQuery, KeyWord

        query = SearchQuery(search_query=str(uuid1()))
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
        query.delete()

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
