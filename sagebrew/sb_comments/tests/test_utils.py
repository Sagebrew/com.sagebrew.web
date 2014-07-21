import pytz
from uuid import uuid1
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from sb_posts.tasks import save_post_task, edit_post_info_task
from sb_posts.utils import save_post, edit_post_info, delete_post_info
from sb_comments.neo_models import SBComment
from sb_comments.utils import save_comment, edit_comment_util, delete_comment_util
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb

class TestComments(TestCase):
    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass


        self.user = User.objects.create_user(
            username='Tyler'+str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

    def test_save_comment(self):
        uuid = str(uuid1())
        post = save_post(post_id=uuid, content="test post", current_pleb=self.pleb.email, wall_pleb=self.pleb.email)
        my_comment = save_comment(content="test comment",pleb=self.pleb.email,post_uuid=post.post_id)

        self.assertEqual(my_comment.content, "test comment")

    def test_edit_comment(self):
        uuid = str(uuid1())
        post = save_post(post_id=uuid, content="test post", current_pleb=self.pleb.email, wall_pleb=self.pleb.email)
        my_comment = save_comment(content="test comment",pleb=self.pleb.email,post_uuid=post.post_id)
        edited_time = datetime.now(pytz.utc)
        edited_comment = edit_comment_util(edited_time,comment_uuid=my_comment.comment_id,content="edited comment")

        self.assertEqual(edited_comment, True)

    def test_delete_comment(self):
        uuid = str(uuid1())
        post = save_post(post_id=uuid, content="test post", current_pleb=self.pleb.email, wall_pleb=self.pleb.email)
        my_comment = save_comment(content="test comment",pleb=self.pleb.email,post_uuid=post.post_id)
        comment_deleted = delete_comment_util(my_comment.comment_id)

        self.assertEqual(comment_deleted, True)
