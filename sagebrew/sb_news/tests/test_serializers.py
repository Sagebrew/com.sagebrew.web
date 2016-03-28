from django.conf import settings
from django.test import TestCase

from neomodel import db

from sb_tags.neo_models import Tag

from sb_news.neo_models import NewsArticle
from sb_news.utils import query_webhose


class TestNewsSerializers(TestCase):
    def setUp(self):
        settings.DEBUG = True

    def tearDown(self):
        settings.DEBUG = False

    def test_no_summary(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        tag = Tag(name="science").save()
        query_webhose(
            None, tag, settings.PROJECT_DIR + "/sb_news/tests/sample_json/"
                                              "no_summary.json")
        tag.delete()
        query = 'MATCH (a:NewsArticle) RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNone(res.one)

    def test_quote_query(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'

        db.cypher_query(query)
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        tag = Tag(name="science").save()
        query_webhose(
            None, tag, settings.PROJECT_DIR + "/sb_news/tests/sample_json/"
                                              "quote_query.json")
        tag.delete()
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c8a3179934b6d4609632383add7fb27ddf3d3842"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNone(res.one['title'], "Breaking: Donald Trump Stuns "
                                            "With Announcement Of Foreign "
                                            "Policy Dream Team")

    def test_site_not_supported(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'

        db.cypher_query(query)
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        tag = Tag(name="science").save()
        query_webhose(
            None, tag, settings.PROJECT_DIR + "/sb_news/tests/sample_json/"
                                              "site_not_supported.json")
        tag.delete()
        query = 'MATCH (a:NewsArticle) RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNone(res.one)

    def test_title_reformat(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'

        db.cypher_query(query)
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        tag = Tag(name="science").save()
        query_webhose(
            None, tag, settings.PROJECT_DIR + "/sb_news/tests/sample_json/"
                                              "title_reformat.json")
        tag.delete()
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c7dd81cf775476d17fd9effe3a43d13d060eb2c8"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNone(res.one['title'], "Obama Welcomes Castro America "
                                            "Criticism: Wouldn't Disagree")
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c294037cba0aad280b655614c5c776f1c5b453ce"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNone(res.one['title'], "Friends Of Israel - "
                                            "The New Yorker")

    def test_title_unique(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'

        db.cypher_query(query)
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        tag = Tag(name="science").save()
        query_webhose(
            None, tag, settings.PROJECT_DIR + "/sb_news/tests/sample_json/"
                                              "title_unique.json")
        tag.delete()
        query = 'MATCH (a:NewsArticle {title: ' \
                '"Sanders\' American Dream Is In Denmark"}) RETURN a'
        res, _ = db.cypher_query(query)
        self.assertEqual(len(res), 1)
        query = 'MATCH (a:NewsArticle {title: ' \
                '"Isis Inc: How Oil Fuels The Jihadi Terrorists - ' \
                'Ft.com"}) RETURN a'
        res, _ = db.cypher_query(query)
        self.assertEqual(len(res), 1)
        query = 'MATCH (a:NewsArticle {title: ' \
                '"Breaking: Donald Trump Stuns With Announcement ' \
                'Of Foreign Policy Dream Team"}) RETURN a'

        res, _ = db.cypher_query(query)
        self.assertEqual(len(res), 1)

    def test_too_close_to_another_article_content(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'

        db.cypher_query(query)
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        tag = Tag(name="science").save()
        query_webhose(
            None, tag,
            settings.PROJECT_DIR + "/sb_news/tests/sample_json/"
                                   "too_close_to_another_article_content.json")
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 5)

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "188ed9cfc6e2214c067ad8e46ec6cd10e392646e"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "32e32ddf8aae3f2ec286ce58b7aac67095b0bbc9"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c11407c888ddbfedca4a56b1aac482d153ad6039"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "d35c1ec82aab431138865043eb9ea511e10fd20c"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "ea6c5a6191f7af36560a107389d8067b748e50ce"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

    def test_too_close_to_another_article_title(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'

        db.cypher_query(query)
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        tag = Tag(name="science").save()
        query_webhose(
            None, tag,
            settings.PROJECT_DIR + "/sb_news/tests/sample_json/"
                                   "too_close_to_another_article_title.json")
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 2)

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "188ed9cfc6e2214c067ad8e46ec6cd10e392646e"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "682408ea92f61d5a44de67ed2aaef7369c401bce"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

    def test_unique_uuid(self):
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'

        db.cypher_query(query)
        query = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        db.cypher_query(query)
        tag = Tag(name="science").save()
        query_webhose(
            None, tag,
            settings.PROJECT_DIR + "/sb_news/tests/sample_json/"
                                   "uuid_unique.json")
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 2)

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "862248ce467c25d9fa20d66e43f13d7f0800882b"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "d35c1ec82aab431138865043eb9ea511e10fd20c"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
