from django.conf import settings
from django.test import TestCase

from neomodel import db

from sb_tags.neo_models import Tag

from sb_news.neo_models import NewsArticle
from sb_news.utils import query_webhose, gather_news_results


class TestNewsSerializers(TestCase):
    """
    NOTE: Did not use mock in this test case because we query images and urls
    within each of the tests. Some of which require redirects and follows. This
    could be completed via mock but was decided to move forward with just the
    demo file approach. This affects a function so there is a TODO to get over
    to mock but please also note that you cannot just use m.stop() after you
    reach out to the mocked url. This results in the system requesting against
    the actual website for w/e reason. So either until this is fixed, modified
    by us, or all the urls are documented and mock endpoints created we'll
    continue to do it this way.
    """
    def setUp(self):
        settings.DEBUG = True

    def tearDown(self):
        settings.DEBUG = False

    def test_no_summary(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "no_summary.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        query = 'MATCH (a:NewsArticle) RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNone(res.one)

    def test_quote_query(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "quote_query.json"

        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c8a3179934b6d4609632383add7fb27ddf3d3842"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertEqual(res.one['title'], "Breaking: Donald Trump Stuns "
                                           "With Announcement Of Foreign "
                                           "Policy Dream Team")

    def test_site_not_supported(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "site_not_supported.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        query = 'MATCH (a:NewsArticle) RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNone(res.one)

    def test_title_reformat(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "title_reformat.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c7dd81cf775476d17fd9effe3a43d13d060eb2c8"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertEqual(res.one['title'], "Obama Welcomes Castro America "
                                           "Criticism: 'Wouldn't Disagree'...")
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c294037cba0aad280b655614c5c776f1c5b453ce"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertEqual(res.one['title'], "Friends Of Israel - "
                                           "The New Yorker")

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c6dd81cf775476d17fd9effe3a43d13d060eb2c8"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertEqual(res.one['title'], "What's This Another New "
                                           "Title It's A Miracle...")

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c8dd81cf775476d17fd9effe3a43d13d060eb2c8"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertEqual(res.one['title'], "Yet Another Title! What Is This!")

    def test_title_unique(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "title_unique.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
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
        test_file = settings.PROJECT_DIR + \
            "/sb_news/tests/sample_json/" \
            "too_close_to_another_article_content.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 2)

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "188ed9cfc6e2214c067ad8e46ec6cd10e392646e"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c11407c888ddbfedca4a56b1aac482d153ad6039"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c11407c888ddbfedca4a56b1aac482d153ad6039"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

    def test_too_close_to_another_article_title(self):
        test_file = settings.PROJECT_DIR + \
            "/sb_news/tests/sample_json/" \
            "too_close_to_another_article_title.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 2)

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "862248ce467c25d9fa20d66e43f13d7f0800882b"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "682408ea92f61d5a44de67ed2aaef7369c401bce"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

    def test_unique_uuid(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "uuid_unique.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 2)

        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "862248ce467c25d9fa20d66e43f13d7f0800882b"}) ' \
                'RETURN a'
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:NewsArticle ' \
                '{external_id: "c11407c888ddbfedca4a56b1aac482d153ad6039"}) ' \
                'RETURN a'

        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

    def test_image_too_close(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "image_too_close.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 1)

    def test_explicit_content(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
            "explicit_content.json"

        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 0)

    def test_non_roman_chars(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "non_roman_chars.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 0)

    def test_excluded_titles(self):
        test_file = settings.PROJECT_DIR + "/sb_news/tests/sample_json/" \
                                           "exclude_titles.json"
        query = 'MATCH (a:NewsArticle) OPTIONAL MATCH (a)-[r]-() ' \
                'DELETE a, r'
        query2 = 'MATCH (a:Tag) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        query3 = 'MATCH (a:UploadedObject) OPTIONAL MATCH (a)-[r]-() ' \
                 'DELETE a, r'
        db.cypher_batch_query([(query, {}), (query2, {}), (query3, {})])
        tag = Tag(name="science").save()
        results = gather_news_results(None, test_file)
        query_webhose(results, tag)
        tag.delete()
        self.assertEqual(len(NewsArticle.nodes.all()), 0)
