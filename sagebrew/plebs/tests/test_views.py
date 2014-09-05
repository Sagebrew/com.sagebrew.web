from uuid import uuid1
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase

from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb
from plebs.views import profile_page

#TODO checkout the 302 vs 200 response codes from circleci

class ProfilePageTest(TestCase):
    fixtures = ["sagebrew/fixtures/initial_data.json"]
    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

    def test_unauthenticated(self):
        request = self.factory.get('/%s' % self.email)
        request.user = AnonymousUser()
        response = profile_page(request, self.email)
        self.assertEqual(response.status_code, 302)

    def test_without_post(self):
        wall = self.pleb.traverse('wall').run()[0]
        posts = wall.traverse('post').run()
        for post in posts:
            post.delete()
        request = self.factory.get('/%s' % self.email)
        request.user = self.user
        response = profile_page(request, self.email)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        test_post = SBPost(content='test', post_id=str(uuid1()))
        test_post.save()
        wall = self.pleb.traverse('wall').run()[0]
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.email)
        request.user = self.user
        response = profile_page(request, self.email)
        self.assertEqual(response.status_code, 200)
        test_post.delete()

    def test_post_with_comments(self):
        test_post = SBPost(content='test', post_id=str(uuid1()))
        test_post.save()
        wall = self.pleb.traverse('wall').run()[0]
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        my_comment = SBComment(content='test comment', comment_id=str(uuid1()))
        my_comment.save()
        rel_to_pleb = my_comment.is_owned_by.connect(self.pleb)
        rel_to_pleb.save()
        rel_from_pleb = self.pleb.comments.connect(my_comment)
        rel_from_pleb.save()
        rel_to_post = my_comment.commented_on_post.connect(test_post)
        rel_to_post.save()
        rel_from_post = test_post.comments.connect(my_comment)
        rel_from_post.save()
        request = self.factory.get('/%s' % self.email)
        request.user = self.user
        response = profile_page(request, self.email)
        self.assertEqual(response.status_code, 200)
        test_post.delete()
        my_comment.delete()

    def test_post_with_comments_from_friend(self):
        test_user = Pleb(email=str(uuid1())+'@gmail.com')
        test_user.save()
        test_post = SBPost(content='test', post_id=str(uuid1()))
        test_post.save()
        wall = self.pleb.traverse('wall').run()[0]
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        my_comment = SBComment(content='test comment', comment_id=str(uuid1()))
        my_comment.save()
        rel_to_pleb = my_comment.is_owned_by.connect(test_user)
        rel_to_pleb.save()
        rel_from_pleb = test_user.comments.connect(my_comment)
        rel_from_pleb.save()
        rel_to_post = my_comment.commented_on_post.connect(test_post)
        rel_to_post.save()
        rel_from_post = test_post.comments.connect(my_comment)
        rel_from_post.save()
        request = self.factory.get('/%s' % self.email)
        request.user = self.user
        response = profile_page(request, self.email)
        self.assertEqual(response.status_code, 200)
        test_user.delete()
        test_post.delete()
        my_comment.delete()

    def test_multiple_posts(self):
        post_array = []
        wall = self.pleb.traverse('wall').run()[0]
        for item in range(0, 50):
            test_post = SBPost(content='test', post_id=str(uuid1()))
            test_post.save()
            test_post.posted_on_wall.connect(wall)
            wall.post.connect(test_post)
            rel = test_post.owned_by.connect(self.pleb)
            rel.save()
            rel_from_pleb = self.pleb.posts.connect(test_post)
            rel_from_pleb.save()
            post_array.append(test_post)
        request = self.factory.get('/%s' % self.email)
        request.user = self.user
        response = profile_page(request, self.email)
        self.assertEqual(response.status_code, 200)
        for post in post_array:
            post.delete()

    def test_multiple_posts_friends(self):
        wall = self.pleb.traverse('wall').run()[0]
        pleb_array = []
        post_array = []
        for item in range(0, 2):
            test_pleb = Pleb(email=str(uuid1())[:32])
            test_pleb.save()
            pleb_array.append(test_pleb)
            for number in range(0, 10):
                test_post = SBPost(content='test', post_id=str(uuid1()))
                test_post.save()
                test_post.posted_on_wall.connect(wall)
                wall.post.connect(test_post)
                rel = test_post.owned_by.connect(test_pleb)
                rel.save()
                rel_from_pleb = test_pleb.posts.connect(test_post)
                rel_from_pleb.save()
                post_array.append(test_post)
        test_post = SBPost(content='test', post_id=str(uuid1()))
        test_post.save()
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.email)
        request.user = self.user
        response = profile_page(request, self.email)
        self.assertEqual(response.status_code, 200)
        for item in pleb_array:
            item.delete()
        for post in post_array:
            post.delete()
        test_post.delete()

    def test_multiple_posts_multiple_comments_friends(self):
        wall = self.pleb.traverse('wall').run()[0]
        pleb_array = []
        post_array = []
        comment_array = []
        for item in range(0, 2):
            test_pleb = Pleb(email=str(uuid1())[:32])
            test_pleb.save()
            pleb_array.append(test_pleb)
            for number in range(0, 10):
                test_post = SBPost(content='test', post_id=str(uuid1()))
                test_post.save()
                test_post.posted_on_wall.connect(wall)
                wall.post.connect(test_post)
                rel = test_post.owned_by.connect(test_pleb)
                rel.save()
                rel_from_pleb = test_pleb.posts.connect(test_post)
                rel_from_pleb.save()
                post_array.append(test_post)
                for num in range(0, 1):
                    my_comment = SBComment(content='test comment',
                                           comment_id=str(uuid1()))
                    my_comment.save()
                    rel_to_pleb = my_comment.is_owned_by.connect(test_pleb)
                    rel_to_pleb.save()
                    rel_from_pleb = test_pleb.comments.connect(my_comment)
                    rel_from_pleb.save()
                    rel_to_post = my_comment.commented_on_post.connect(
                        test_post)
                    rel_to_post.save()
                    rel_from_post = test_post.comments.connect(my_comment)
                    rel_from_post.save()
                    comment_array.append(my_comment)
                    my_comment = SBComment(content='test comment',
                                           comment_id=str(uuid1()))
                    my_comment.save()
                    rel_to_pleb = my_comment.is_owned_by.connect(self.pleb)
                    rel_to_pleb.save()
                    rel_from_pleb = self.pleb.comments.connect(my_comment)
                    rel_from_pleb.save()
                    rel_to_post = my_comment.commented_on_post.connect(
                        test_post)
                    rel_to_post.save()
                    rel_from_post = test_post.comments.connect(my_comment)
                    rel_from_post.save()
                    comment_array.append(my_comment)
        test_post = SBPost(content='test', post_id=str(uuid1()))
        test_post.save()
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.email)
        request.user = self.user
        response = profile_page(request, self.email)
        self.assertEqual(response.status_code, 200)
        for item in pleb_array:
            item.delete()
        for post in post_array:
            post.delete()
        for comment in comment_array:
            comment.delete()
        test_post.delete()

#TODO test friend user, registered non-friend user getting the correct page


