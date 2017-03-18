from django.conf import settings
from django.test import TestCase

from neomodel import db

from sagebrew.sb_tags.neo_models import Tag

from sagebrew.sb_news.tasks import find_tag_news


class TestNewsTasks(TestCase):

    def setUp(self):
        settings.DEBUG = True
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.DEBUG = False
        settings.CELERY_ALWAYS_EAGER = False

    def test_find_tag_news_no_tags(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        res = find_tag_news.apply_async()
        self.assertTrue(res.result)

    def test_find_tag_news_one_tag(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'

        db.cypher_query(query)
        tag = Tag(name="science").save()
        res = find_tag_news.apply_async()
        tag.delete()
        self.assertTrue(res.result)
