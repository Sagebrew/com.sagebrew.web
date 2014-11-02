from uuid import uuid1
from django.test import TestCase

from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost
from sb_garbage.neo_models import SBGarbageCan
from sb_garbage.utils import delete_posts_util, delete_comments_util

class TestDeleteCommentUtil(TestCase):
    def setUp(self):
        self.comment = SBComment(sb_id=str(uuid1()),
                                 content=str(uuid1()), to_be_deleted=True)
        self.comment.save()
        try:
            self.garbage = SBGarbageCan.nodes.get(garbage_can='garbage')
        except SBGarbageCan.DoesNotExist:
            self.garbage = SBGarbageCan(garbage_can='garbage').save()

        self.garbage.comments.connect(self.comment)

    def test_delete_comment_util_success(self):
        res = delete_comments_util(self.garbage)

        self.assertTrue(res)


class TestDeletePostUtil(TestCase):
    def setUp(self):
        self.post = SBPost(sb_id=str(uuid1()),
                                 content=str(uuid1()), to_be_deleted=True)
        self.post.save()
        try:
            self.garbage = SBGarbageCan.nodes.get(garbage_can='garbage')
        except SBGarbageCan.DoesNotExist:
            self.garbage = SBGarbageCan(garbage_can='garbage').save()

        self.garbage.posts.connect(self.post)

    def test_delete_post_util_success(self):
        res = delete_posts_util(self.garbage)

        self.assertTrue(res)
