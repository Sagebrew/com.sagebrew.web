from uuid import uuid1
import pytz
from datetime import datetime

from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from sb_registration.utils import create_user_util_test

from sb_news.neo_models import NewsArticle


class QuestEndpointTests(APITestCase):

    def setUp(self):
        query = "match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        cache.clear()

    def test_unauthorized(self):
        url = reverse('news-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('news-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        self.client.force_authenticate(user=self.user)
        url = reverse('news-list')
        data = {
            "provider": "sb_crawler",
            "external_id": str(uuid1()),
            "url": "https://www.sagebrew.com",
            "site_full": "https://www.sagebrew.com",
            "site_section": "site_section",
            "title": "This is the title",
            "title_full": "A full title",
            "content": "This is some fake content",
            "language": "en",
            "published": datetime.now(pytz.utc),
            "country": "US",
            "spam_score": 0.0,
            "image": "https://sagebrew-master.s3.amazonaws.com/"
                     "profile_pictures/"
                     "8a274be8-71ee-259c-32fc-c3269a5adf9b-198x200.png",
            "performance_score": 10,
            "crawled": datetime.now(pytz.utc),
        }
        response = self.client.post(url, data=data, format='json')
        news = NewsArticle.nodes.get(external_id=response.data['external_id'])
        news.delete()
        self.assertEqual(news.title, "This Is The Title")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        self.client.force_authenticate(user=self.user)
        url = reverse('news-list')
        data = {
            "provider": "sb_crawler",
            "external_id": str(uuid1()),
            "url": "https://www.sagebrew.com",
            "site_full": "https://www.sagebrew.com",
            "site_section": "site_section",
            "title": "This is the title",
            "content": "This is some fake content",
            "title_full": "A full title",
            "language": "en",
            "published": datetime.now(pytz.utc),
            "country": "US",
            "spam_score": 0.0,
            "image": "https://sagebrew-master.s3.amazonaws.com/"
                     "profile_pictures/"
                     "8a274be8-71ee-259c-32fc-c3269a5adf9b-198x200.png",
            "performance_score": 10,
            "crawled": datetime.now(pytz.utc),
        }
        self.client.post(url, data=data, format='json')
        response = self.client.get(url, format='json')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        self.client.force_authenticate(user=self.user)
        url = reverse('news-list')
        data = {
            "provider": "sb_crawler",
            "external_id": str(uuid1()),
            "url": "https://www.sagebrew.com",
            "site_full": "https://www.sagebrew.com",
            "site_section": "site_section",
            "title": "This is the title",
            "content": "This is some fake content",
            "title_full": "A full title",
            "language": "en",
            "published": datetime.now(pytz.utc),
            "country": "US",
            "spam_score": 0.0,
            "image": "https://sagebrew-master.s3.amazonaws.com/"
                     "profile_pictures/"
                     "8a274be8-71ee-259c-32fc-c3269a5adf9b-198x200.png",
            "performance_score": 10,
            "crawled": datetime.now(pytz.utc),
        }
        response = self.client.post(url, data=data, format='json')
        url = reverse('news-detail',
                      kwargs={"object_uuid": response.data['id']})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['title'], 'This Is The Title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
