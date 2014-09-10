from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from elasticsearch import Elasticsearch

from api.tasks import add_object_to_search_index
from plebs.neo_models import Pleb
from sb_search.views import search_result_api

class TestSearchResultAPI(TestCase):
    def setUp(self):
        try:
            pleb = Pleb.index.get(email=str(uuid1()) + '@gmail.com')
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email=str(uuid1()) + '@gmail.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email=str(uuid1()) + '@gmail.com')


    def test_search_result_api_success(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res_array = []
        for item in range(0,9):
            res = es.index(index='full-search-user-specific-1',
                           doc_type='sb_test',
                           body={'content': 'test content'})
            res_array.append(res)

        request = self.factory.get('/search/q=test')
        request.user = self.user

        response = search_result_api(request)
        response = response.render()
        print response
        self.assertEqual(response.status_code, 200)