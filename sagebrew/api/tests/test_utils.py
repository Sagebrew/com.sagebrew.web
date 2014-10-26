from uuid import uuid1
from django.test import TestCase

from api.utils import (post_to_garbage, comment_to_garbage, language_filter)
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment
from sb_garbage.neo_models import SBGarbageCan

class TestPostToGarbageUtil(TestCase):
    def setUp(self):
        try:
            self.garbage = SBGarbageCan.nodes.get(garbage_can='garbage')
        except SBGarbageCan.DoesNotExist:
            self.garbage = SBGarbageCan(garbage_can='garbage').save()

        self.post = SBPost(post_id=str(uuid1())).save()

    def test_post_to_garbage_garbage_exists(self):
        res = post_to_garbage(self.post.post_id)

        self.assertTrue(res)

    def test_post_to_garbage_garbage_does_not_exist(self):
        self.garbage.delete()

        res = post_to_garbage(self.post.post_id)

        self.assertTrue(res)

    def test_post_to_garbage_post_has_comments(self):
        comment = SBComment(comment_id=str(uuid1())).save()
        self.post.comments.connect(comment)

        res = post_to_garbage(self.post.post_id)

        self.assertTrue(res)

    def test_post_to_garbage_post_does_not_exist(self):
        res = post_to_garbage(str(uuid1()))

        self.assertTrue(res)


class TestCommentToGarbageUtil(TestCase):
    def setUp(self):
        try:
            self.garbage = SBGarbageCan.nodes.get(garbage_can='garbage')
        except SBGarbageCan.DoesNotExist:
            self.garbage = SBGarbageCan(garbage_can='garbage').save()

        self.comment = SBComment(comment_id=str(uuid1())).save()

    def test_comment_to_garbage_garbage_exists(self):
        res = comment_to_garbage(self.comment.comment_id)

        self.assertTrue(res)

    def test_comment_to_garbage_garbage_does_not_exist(self):
        self.garbage.delete()

        res = comment_to_garbage(self.comment.comment_id)

        self.assertTrue(res)

    def test_comment_to_garbage_comment_does_not_exist(self):
        res = comment_to_garbage(str(uuid1()))

        self.assertTrue(res)


class TestLanguageFilterUtil(TestCase):
    def setUp(self):
        self.vulgar_words = 'anal anus ballsack blowjob blow job boner'

    def test_language_filter(self):
        res = language_filter(self.vulgar_words)

        self.assertNotEqual(res, self.vulgar_words)

    def test_language_filter_not_profane(self):
        sentence = "The quick brown fox jumped over the lazy dog."

        res = language_filter(sentence)

        self.assertEqual(res, sentence)


class