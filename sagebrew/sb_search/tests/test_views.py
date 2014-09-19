from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command

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
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

'''
    def test_search_result_api_success(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res_array = []
        for item in range(0,9):
            res = es.index(index='full-search-user-specific-1',
                           doc_type='sb_test',
                           body={'content': 'test content'})
            res_array.append(res)

        request = self.factory.get('/search/q=test&page=1')
        request.user = self.user

        response = search_result_api(request)

        self.assertEqual(response.status_code, 200)
'''

