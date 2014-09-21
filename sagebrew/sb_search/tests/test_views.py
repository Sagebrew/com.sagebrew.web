from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse

from elasticsearch import Elasticsearch

from api.tasks import add_object_to_search_index
from plebs.neo_models import Pleb
from sb_search.views import search_result_api, search_result_view

class TestSearchResultView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_search_result_view_success(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test')

        self.assertEqual(response.status_code, 200)

    def test_search_result_view_missing_data(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        self.assertRaises(TypeError, search_result_view, request)

    def test_search_result_incorrect_data_page_string(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', page='string')

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_page_list(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', page=[])

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_page_dict(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', page={})

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_page_float(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', page=8.51651)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_page_image(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', page=image)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_display_num_string(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', display_num='string')

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_display_num_list(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', display_num=[])

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_display_num_dict(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', display_num={})

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_display_num_float(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', display_num=8.51651)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_display_num_image(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', display_num=image)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_query_list(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, [], page=1)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_query_dict(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, {}, page=1)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_start_string(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_start='string')

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_start_list(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_start=[])

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_start_dict(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_start={})

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_start_float(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_start=8.51651)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_start_image(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_start=image)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_end_string(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_end='string')

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_end_list(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_end=[])

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_end_dict(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_end={})

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_end_float(self):
        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_end=8.51651)

        self.assertEqual(response.status_code, 400)

    def test_search_result_incorrect_data_range_end_image(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/search/q=test')
        request.user = self.user

        response = search_result_view(request, 'test', range_end=image)

        self.assertEqual(response.status_code, 400)


class TestSearchResultAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com',
            password='password')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_search_result_api_success(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res_array = []
        for item in range(0,9):
            res = es.index(index='full-search-user-specific-1',
                           doc_type='sb_test',
                           body={'content': 'test content'})
            res_array.append(res)

        self.client.login(username='Tyler', password='password')
        request = self.client.get(reverse('search_result_api',kwargs={'query_param':'test', 'page': '1'}))

        self.assertEqual(request.status_code, 200)

    def test_search_result_api_failure_unauthenticated(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res_array = []
        for item in range(0,9):
            res = es.index(index='full-search-user-specific-1',
                           doc_type='sb_test',
                           body={'content': 'test content'})
            res_array.append(res)

        self.client.login(username='Tyler', password='asdfa')
        request = self.client.get(reverse('search_result_api',kwargs={'query_param':'test', 'page': '1'}))

        self.assertEqual(request.status_code, 401)

class TestSearchResultAPIReturns(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email="tyler"+str(uuid1())[:8]+'@gmail.com',
            password='password')

    def tearDown(self):
        call_command('clear_neo_db')
        #TODO make this test create actual questions so that there is actual
        #html that can be returned and checked to make sure what I am getting
        #back is what I actually want
'''
    def test_search_result_api_returns_expected(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.index(index='full-search-user-specific-1',
                 doc_type='question',
                 body={
                     'question_title': 'Are current battery-powered cars really'
                                       ' more eco-friendly than cars that run '
                                       'off fossil fuels?',
                     'question_content': 'There have been mixed reviews as to '
                                         'whether or not battery-powered cars '
                                         'are actually more eco-friendly, as '
                                         'they claim to be. On one side of the '
                                         'equation, battery powered cars give '
                                         'off no fuel emissions, meaning no '
                                         'carbon dioxide or other greenhouse '
                                         'gasses that have been shown to '
                                         'negatively impact the balance of the '
                                         'environment. On the other side, the '
                                         'process by which electric cars are '
                                         'made, in addition to the electricity '
                                         'needed to power them, are both heavy '
                                         'proponents of greenhouse gas '
                                         'emissions. ',
                     'related_user': self.user.email
                 })
        es.index(index='full-search-user-specific-1',
                 doc_type='question',
                 body={
                     'question_title': 'How can we reduce the amount of NO2 '
                                       'pollution in the atmosphere?',
                     'question_content': 'NO2 is a greenhouse gas 300 times '
                                         'more harmful to the environment than '
                                         'CO2, and the levels of NO2 in the '
                                         'environment are rising far above '
                                         'average atmospheric fluctuation. '
                                         'What are some of the causes of this '
                                         'and what can we do to reduce the '
                                         'amount of NO2 being placed into the '
                                         'atmosphere? ',
                     'related_user': self.user.email
                 })
        self.client.login(username='Tyler', password='password')
        request = self.client.get(reverse('search_result_api',kwargs={'query_param':'reduce', 'page': '1'}))
        self.assertEqual(request.status_code, 200)
'''