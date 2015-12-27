from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory
from elasticsearch import Elasticsearch

from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo
from sb_registration.utils import create_user_util_test

from sb_search.utils import (remove_search_object)


class TestRemoveSearchObject(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_success(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.index(index='full-search-base', doc_type='pleb',
                 id=self.pleb.username, body=PlebSerializerNeo(self.pleb).data)
        res = remove_search_object(self.pleb.username, 'pleb')
        self.assertTrue(res)
