import pytz
import time
import shortuuid
from json import loads
from datetime import datetime
from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from elasticsearch import Elasticsearch

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_search.views import search_result_view
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util_test


class TestSearchResultView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.save()

    def test_search_result_view_success(self):
        request = self.factory.post('/search/?q=test')
        request.user = self.user

        response = search_result_view(request)

        self.assertEqual(response.status_code, 200)


class TestSearchResultAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_search_result_api_success(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res_array = []
        for item in range(0,9):
            res = es.index(index='full-search-user-specific-1',
                           doc_type='pleb',
                           body={'content': 'test content'})
            res_array.append(res)

        self.client.login(username=self.user.username,
                          password='testpassword')
        request = self.client.get(reverse('search_result_api')+"?q=test")

        self.assertEqual(request.status_code, 200)

    def test_search_result_api_failure_unauthenticated(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res_array = []
        for item in range(0,9):
            res = es.index(index='full-search-user-specific-1',
                           doc_type='pleb',
                           body={'content': 'test content'})
            res_array.append(res)

        self.client.login(username=self.user.username, password='asdfa')
        request = self.client.get(reverse('search_result_api'))

        self.assertEqual(request.status_code, 401)


class TestSearchResultAPIReturns(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name='Tyler'
        self.pleb.last_name='Wiersing'
        self.pleb.save()
        self.q1dict = {'title': 'Are current battery-powered '
                                    'cars really more eco-friendly '
                                    'than cars that run '
                                    'off fossil fuels?',
                        'question_content': 'There have been mixed reviews'
                                      ' as to whether or not '
                                      'battery-powered cars are '
                                      'actually more eco-friendly, '
                                      'as they claim to be. On one '
                                      'side of the equation, battery'
                                      ' powered cars give off no '
                                      'fuel emissions, meaning no '
                                      'carbon dioxide or other '
                                      'greenhouse gasses that have '
                                      'been shown to negatively '
                                      'impact the balance of the '
                                      'environment. On the other '
                                      'side, the process by which '
                                      'electric cars are made, in '
                                      'addition to the electricity '
                                      'needed to power them, are '
                                      'both heavy proponents of '
                                      'greenhouse gas emissions. '}
        self.q2dict = {'title': 'How can we reduce the amount of'
                                         ' NO2 pollution in the '
                                         'atmosphere?',
                       'question_content':  'NO2 is a greenhouse gas 300 '
                                            'times more harmful to the '
                                            'environment than CO2, and the'
                                            ' levels of NO2 in the '
                                            'environment are rising '
                                            'far above average atmospheric'
                                            ' fluctuation. What are some '
                                            'of the causes of this and '
                                            'what can we do to reduce the '
                                            'amount of NO2 being placed '
                                            'into the atmosphere? '}

    def tearDown(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.delete_by_query('full-search-user-specific-1',
                           'sb_questions.neo_models.SBQuestion',
                           body={
                               'query': {
                                   'query_string': {
                                       'query': 'batter-powered'
                                   }
                               }
                           })

    def test_search_result_api_returns_expected(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        question1 = SBQuestion(object_uuid=str(uuid1()),
                               title=self.q1dict['title'],
                               content=self.q1dict['question_content'],
                               is_closed=False, solution_count=0,
                               last_edited_on=datetime.now(pytz.utc),
                               upvotes=0,
                               downvotes=0,
                               created=datetime.now(pytz.utc))
        question1.save()
        question1.owned_by.connect(self.pleb)
        index_res = es.index(index='full-search-user-specific-1',
                             doc_type='sb_questions.neo_models.SBQuestion',
                             body={
                                 'object_uuid': question1.object_uuid,
                                 'title': question1.title,
                                 'question_content': question1.content,
                                 'related_user': self.user.username
                             })
        self.assertTrue(index_res['created'])
        time.sleep(2)
        self.client.login(username=self.user.username,
                          password='testpassword')
        request = self.client.get('/search/api/?q=battery-powered')
        self.assertEqual(request.status_code, 200)
        self.assertIn('question_uuid', request.content)

    def test_search_result_api_returns_multi_expected(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        question1 = SBQuestion(object_uuid=str(uuid1()),
                               title=self.q1dict['title'],
                               content=self.q1dict['question_content'],
                               is_closed=False, solution_count=0,
                               last_edited_on=datetime.now(pytz.utc),
                               upvotes=0,
                               downvotes=0,
                               created=datetime.now(pytz.utc))
        question1.save()
        question1.owned_by.connect(self.pleb)
        es.index(index='full-search-user-specific-1',
                 doc_type='sb_questions.neo_models.SBQuestion',
                 body={
                     'object_uuid': question1.object_uuid,
                     'title': question1.title,
                     'question_content': question1.content,
                     'related_user': self.user.username
                 })
        for item in range(0,9):
            es.index(index='full-search-user-specific-1',
                     doc_type='sb_questions.neo_models.SBQuestion',
                     body={
                         'object_uuid': question1.object_uuid,
                         'title': question1.title,
                         'question_content': question1.content,
                         'related_user': self.user.username
                     })
        time.sleep(2)
        self.client.login(username=self.user.username, password='testpassword')
        request = self.client.get('/search/api/?q=battery-powered')
        self.assertGreaterEqual(len(loads(request.content)['html']), 1)
        self.assertEqual(request.status_code, 200)
        self.assertIn('question_uuid', request.content)

    def test_search_result_api_returns_page_2(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        question1 = SBQuestion(object_uuid=str(uuid1()),
                               title=self.q1dict['title'],
                               content=self.q1dict['question_content'],
                               is_closed=False, solution_count=0,
                               last_edited_on=datetime.now(pytz.utc),
                               upvotes=0,
                               downvotes=0,
                               created=datetime.now(pytz.utc))
        question1.save()
        question1.owned_by.connect(self.pleb)
        es.index(index='full-search-user-specific-1',
                 doc_type='sb_questions.neo_models.SBQuestion',
                 body={
                     'object_uuid': question1.object_uuid,
                     'title': question1.title,
                     'question_content': question1.content,
                     'related_user': self.user.username
                 })
        for item in range(0,19):
            es.index(index='full-search-user-specific-1',
                     doc_type='sb_questions.neo_models.SBQuestion',
                     body={
                         'object_uuid': question1.object_uuid,
                         'title': question1.title,
                         'question_content': question1.content,
                         'related_user': self.user.username
                     })
        time.sleep(2)
        self.client.login(username=self.user.username, password='testpassword')
        request = self.client.get('/search/api/?q=battery-powered&page=2')

        self.assertEqual(len(loads(request.content)['html']), 10)
        self.assertEqual(request.status_code, 200)

    def test_search_result_api_returns_page_3(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        question1 = SBQuestion(object_uuid=str(uuid1()),
                               title=self.q1dict['title'],
                               question_content=self.q1dict['question_content'],
                               is_closed=False, solution_count=0,
                               last_edited_on=datetime.now(pytz.utc),
                               upvotes=0,
                               downvotes=0,
                               created=datetime.now(pytz.utc))
        question1.save()
        question1.owned_by.connect(self.pleb)
        es_res = es.index(index='full-search-user-specific-1',
                 doc_type='sb_questions.neo_models.SBQuestion',
                 body={
                     'object_uuid': question1.object_uuid,
                     'title': question1.title,
                     'question_content': question1.question_content,
                     'related_user': self.user.username
                 })
        for item in range(0,39):
            es.index(index='full-search-user-specific-1',
                     doc_type='sb_questions.neo_models.SBQuestion',
                     body={
                         'object_uuid': question1.object_uuid,
                         'title': question1.title,
                         'question_content': question1.question_content,
                         'related_user': self.user.username
                     })
        time.sleep(3)

        self.client.login(username=self.user.username, password='testpassword')
        request = self.client.get('/search/api/?q=battery-powered&page=3')
        self.assertEqual(len(loads(request.content)['html']), 10)
        self.assertEqual(request.status_code, 200)

    def test_search_result_api_result_user_has_no_results(self):
        email = str(uuid1()).strip('-')+"@gmail.com"
        pleb = Pleb(email=email)
        pleb.save()
        user = User.objects.create_user(shortuuid.uuid(), email, 'testpassword')
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        question1 = SBQuestion(object_uuid=str(uuid1()),
                               title=self.q1dict['title'],
                               question_content=self.q1dict['question_content'],
                               is_closed=False, solution_count=0,
                               last_edited_on=datetime.now(pytz.utc),
                               upvotes=0,
                               downvotes=0,
                               created=datetime.now(pytz.utc))
        question1.save()
        question1.owned_by.connect(self.pleb)
        es.index(index='full-search-user-specific-1',
                 doc_type='sb_questions.neo_models.SBQuestion',
                 body={
                     'object_uuid': question1.object_uuid,
                     'title': question1.title,
                     'question_content': question1.question_content,
                     'related_user': str(uuid1()).strip('-')
                 })
        for item in range(0,29):
            es.index(index='full-search-user-specific-1',
                     doc_type='sb_questions.neo_models.SBQuestion',
                     body={
                         'object_uuid': question1.object_uuid,
                         'title': question1.title,
                         'question_content': question1.question_content,
                         'related_user': str(uuid1()).strip('-')
                     })
        time.sleep(2)
        self.client.login(username=user.username, password='testpassword')
        request = self.client.get('/search/api/?q=battery-powered')

        self.assertEqual(request.status_code, 200)
        self.assertIn('<div>Sorry! There seems to be nothing here!</div>',
                      request.content)

    def test_search_result_api_similar_questions_and_query(self):
        email = '%s%s'%(str(uuid1()).replace("-", ""), '@gmail.com')
        pleb = Pleb(email=email)
        pleb.save()
        self.user.email = email
        self.user.save()
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        question1 = SBQuestion(object_uuid=str(uuid1()),
                               title=self.q1dict['title'],
                               content=self.q1dict['question_content'],
                               is_closed=False, solution_count=0,
                               last_edited_on=datetime.now(pytz.utc),
                               upvotes=0,
                               downvotes=0,
                               created=datetime.now(pytz.utc))
        question1.save()
        question1.owned_by.connect(pleb)
        es.index(index='full-search-user-specific-1',
                 doc_type='sb_questions.neo_models.SBQuestion',
                 body={
                     'object_uuid': question1.object_uuid,
                     'title': question1.title,
                     'question_content': question1.content,
                     'related_user': self.user.username
                 })

        question2 = SBQuestion(object_uuid=str(uuid1()),
                               title='Should we ban the use '
                                              'of fossil fuels?',
                               content='With battery-powered cars '
                                                'becoming more and more '
                                                'efficient and affordable'
                                                'and home energy solutions '
                                                'such as solar or natural '
                                                'gas becoming more feasible '
                                                'and popular, would it '
                                                'be better for us to ban '
                                                'use of fossil fuels? '
                                                'What could we use instead of'
                                                'fossil fuels?',
                               )
        question2.save()
        es.index(index='full-search-user-specific-1',
                 doc_type='sb_questions.neo_models.SBQuestion',
                 body={'object_uuid': question2.object_uuid,
                       'question_content': question2.content,
                       'title': question2.title,
                       'related_user': self.user.username})
        time.sleep(3)
        self.client.login(username=self.user.username, password='testpassword')
        request = self.client.get('/search/api/?q=fossil fuels')
        result_dict = loads(request.content)

        res1 = SBQuestion.nodes.get(object_uuid=result_dict['html'][0]['question_uuid'])
        res2 = SBQuestion.nodes.get(object_uuid=result_dict['html'][1]['question_uuid'])
        self.assertEqual(res1.title, question2.title)
        self.assertEqual(res2.title, question1.title)
        self.assertEqual(request.status_code, 200)


'''
question2 = SBQuestion(object_uuid=str(uuid1()),
                       title='How can we reduce the amount of'
                                      ' NO2 pollution in the '
                                      'atmosphere?',
                       question_content='NO2 is a greenhouse gas 300 '
                                        'times more harmful to the '
                                        'environment than CO2, and the'
                                        ' levels of NO2 in the '
                                        'environment are rising '
                                        'far above average atmospheric'
                                        ' fluctuation. What are some '
                                        'of the causes of this and '
                                        'what can we do to reduce the '
                                        'amount of NO2 being placed '
                                        'into the atmosphere? ')
question2.save()
question2.owned_by.connect(self.pleb)
es.index(index='full-search-user-specific-1',
         doc_type='question',
         body={
             'question_uuid': question2.object_uuid,
             'title': question2.title,
             'question_content': question2.question_content,
             'related_user': self.user.email
         })
'''