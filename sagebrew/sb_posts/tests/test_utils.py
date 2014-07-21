from uuid import uuid1

from django.test import TestCase
from django.contrib.auth.models import User

from sb_posts.tasks import save_post_task, edit_post_info_task
from sb_posts.utils import save_post, edit_post_info, delete_post_info, create_post_vote
from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb


class TestSavePost(TestCase):
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

    def test_save_post(self):
        poster = Pleb.index.get(email=self.pleb.email)
        uuid = str(uuid1())
        post = save_post(post_id=uuid, content="test post", current_pleb=self.pleb.email, wall_pleb=self.pleb.email)
        wall = post.traverse('posted_on_wall').run()[0]

        self.assertEqual(poster.email, post.traverse('owned_by').run()[0].email)
        self.assertEqual(wall, self.pleb.traverse('wall').run()[0])
        self.assertEqual("test post", post.content)
        self.assertEqual(post.post_id, uuid)
        post.delete()

    def test_post_already_exists(self):
        post_info_dict = {'current_pleb': self.pleb.email,
                          'wall_pleb': self.pleb.email,
                          'content': 'test post',
                          'post_id': str(uuid1())}

        prev_post = SBPost(content='test', post_id=post_info_dict['post_id'])
        prev_post.save()
        post = save_post(post_id=post_info_dict['post_id'], content='test post', current_pleb=self.pleb.email, wall_pleb=self.pleb.email)
        self.assertEqual(post, None)

    def test_edit_post(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', post_id=uuid, current_pleb=self.pleb.email, wall_pleb=self.pleb.email)
        test_post.save()
        edited_post = edit_post_info(content='post edited',post_uuid=uuid)

        self.assertEqual(edited_post.content, 'post edited')

    def test_delete_post(self):
        uuid = str(uuid1())
        test_post = SBPost(content='test', post_id=uuid, current_pleb=self.pleb.email, wall_pleb=self.pleb.email)
        test_post.save()
        if delete_post_info(uuid):
            try:
                post = SBPost.index.get(post_id = uuid)
            except SBPost.DoesNotExist:
                print "Post deleted"
                return

class TestPostVotes(TestCase):
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

    def test_upvote_post(self):
        uuid = str(uuid1())
        post = save_post(post_id=uuid, content="test post", current_pleb=self.pleb.email, wall_pleb=self.pleb.email)
        create_post_vote(pleb=self.pleb.email,post_uuid=post.post_id,vote_type='up')

        self.assertEqual(post.up_vote_number, 1)
