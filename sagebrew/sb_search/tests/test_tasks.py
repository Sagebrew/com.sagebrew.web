import time
import pickle
from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import RequestFactory

from elasticsearch import Elasticsearch

from plebs.neo_models import Pleb
from sb_search.tasks import (update_search_query, create_keyword,
                             update_search_object)
from sb_registration.utils import create_user_util_test
from plebs.serializers import PlebSerializerNeo
from sb_quests.serializers import QuestSerializer
from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_solutions.neo_models import Solution
from sb_solutions.serializers import SolutionSerializerNeo


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
            "username": str(uuid1()), "query_param": test_query.search_query,
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
            "username": str(uuid1()), "query_param": test_query.search_query,
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
            "username": self.pleb.username,
            "query_param": test_query.search_query,
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
            "username": self.pleb.username,
            "query_param": test_query.search_query,
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_update_search_query_query_does_not_exist(self):
        task_data = {
            "username": self.pleb.username,
            "query_param": str(uuid1()),
            "keywords": ['fake', 'keywords']
        }

        res = update_search_query.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)


class TestCreateKeywordTask(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
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


class TestUpdateSearchObject(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        self.es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)

    def test_question(self):
        question = Question(title=str(uuid1()),
                            content="some test content",).save()
        question.owned_by.connect(self.pleb)
        question.owner_username = self.pleb.username
        object_data = QuestionSerializerNeo(question).data
        res = self.es.index(index='full-search-base', doc_type='question',
                            id=question.object_uuid, body=object_data)
        self.assertTrue(res['created'])
        question.content = "this is post save content that will be tested"
        question.save()
        task_data = {
            "object_uuid": question.object_uuid,
            "label": "question"
        }
        res = update_search_object.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        res = self.es.get(index="full-search-base", doc_type="question",
                          id=question.object_uuid)

        self.assertEqual('this is post save content that will be tested',
                         res['_source']['content'])

    def test_pleb(self):
        object_data = PlebSerializerNeo(self.pleb).data
        self.es.index(index='full-search-base', doc_type='profile',
                      id=self.pleb.object_uuid, body=object_data)
        self.pleb.profile_pic = str(uuid1())
        self.pleb.save()
        task_data = {
            "object_uuid": self.pleb.object_uuid,
            "label": "pleb"
        }
        res = update_search_object.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        res = self.es.get(index="full-search-base", doc_type="profile",
                          id=self.pleb.object_uuid)

        self.assertEqual(self.pleb.profile_pic, res['_source']['profile_pic'])

    def test_quest(self):
        quest = Quest().save()
        quest.owner.connect(self.pleb)
        quest.owner_username = self.pleb.username
        object_data = QuestSerializer(quest).data
        res = self.es.index(index='full-search-base',
                            doc_type=object_data['type'],
                            id=quest.object_uuid,
                            body=object_data)
        self.assertTrue(res['created'])
        quest.profile_pic = str(uuid1())
        quest.save()
        task_data = {
            "object_uuid": quest.object_uuid,
            "label": "quest"
        }
        res = update_search_object.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        res = self.es.get(index="full-search-base",
                          doc_type=object_data['type'],
                          id=quest.object_uuid)

        self.assertEqual(quest.profile_pic, res['_source']['profile_pic'])

    def test_mission(self):
        mission = Mission().save()
        mission.owner_username = self.pleb.username
        object_data = MissionSerializer(mission).data
        res = self.es.index(index='full-search-base',
                            doc_type=object_data['type'],
                            id=mission.object_uuid,
                            body=object_data)
        self.assertTrue(res['created'])
        mission.about = str(uuid1())
        mission.save()
        task_data = {
            "object_uuid": mission.object_uuid,
            "label": "mission"
        }
        res = update_search_object.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        res = self.es.get(index="full-search-base",
                          doc_type=object_data['type'],
                          id=mission.object_uuid)

        self.assertEqual(mission.about, res['_source']['about'])

    def test_not_valid(self):
        request = RequestFactory().get('')
        request.user = self.user
        question = Question(
            content="hello", owner_username=self.pleb.username,
            title=str(uuid1())).save()
        solution = Solution(parent_id=question.object_uuid).save()
        question.solutions.connect(solution)
        solution.owner_username = self.pleb.username

        object_data = SolutionSerializerNeo(solution,
                                            context={"request": request}).data
        res = self.es.index(index='full-search-base',
                            doc_type=object_data['type'],
                            id=solution.object_uuid,
                            body=object_data)
        self.assertTrue(res['created'])
        solution.content = str(uuid1())
        solution.save()
        task_data = {
            "object_uuid": solution.object_uuid,
            "label": "solution"
        }
        res = update_search_object.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)

    def test_no_label(self):
        request = RequestFactory().get('')
        request.user = self.user
        question = Question(title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        object_data = QuestionSerializerNeo(question,
                                            context={"request": request}).data
        res = self.es.index(index='full-search-base',
                            doc_type=object_data['type'],
                            id=question.object_uuid,
                            body=object_data)
        self.assertTrue(res['created'])
        question.content = str(uuid1())
        question.save()
        task_data = {
            "object_uuid": question.object_uuid
        }
        res = update_search_object.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        res = self.es.get(index="full-search-base", doc_type="question",
                          id=question.object_uuid)

        self.assertEqual(question.content,
                         res['_source']['content'])

    def test_no_label_not_question(self):
        request = RequestFactory().get('')
        request.user = self.user
        question = Question(
            content="hello", owner_username=self.pleb.username,
            title=str(uuid1())
        ).save()
        solution = Solution(parent_id=question.object_uuid).save()
        question.solutions.connect(solution)
        solution.owner_username = self.pleb.username
        object_data = SolutionSerializerNeo(solution,
                                            context={"request": request}).data
        res = self.es.index(index='full-search-base',
                            doc_type=object_data['type'],
                            id=solution.object_uuid,
                            body=object_data)
        self.assertTrue(res['created'])
        solution.content = str(uuid1())
        solution.save()
        task_data = {
            "object_uuid": solution.object_uuid
        }
        res = update_search_object.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)
