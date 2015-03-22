from uuid import uuid1
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb
from plebs.views import (profile_page, friends_page, about_page,
                         reputation_page)
from sb_registration.utils import create_user_util_test
from api.utils import wait_util


class ProfilePageTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()

    def test_unauthenticated(self):
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = AnonymousUser()
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 302)

    def test_without_post(self):
        wall = self.pleb.wall.all()[0]
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)

    def test_with_post(self):
        test_post = SBPost(content='test', object_uuid=str(uuid1()))
        test_post.save()
        wall = self.pleb.wall.all()[0]
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)
        test_post.delete()

    def test_post_with_comments(self):
        test_post = SBPost(content='test', object_uuid=str(uuid1()))
        test_post.save()
        wall = self.pleb.wall.all()[0]
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        my_comment = SBComment(content='test comment', object_uuid=str(uuid1()))
        my_comment.save()
        rel_to_pleb = my_comment.is_owned_by.connect(self.pleb)
        rel_to_pleb.save()
        rel_from_pleb = self.pleb.comments.connect(my_comment)
        rel_from_pleb.save()
        rel_from_post = test_post.comments.connect(my_comment)
        rel_from_post.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)
        test_post.delete()
        my_comment.delete()

    def test_post_with_comments_from_friend(self):
        test_user = Pleb(email=str(uuid1())+'@gmail.com')
        test_user.save()
        test_post = SBPost(content='test', object_uuid=str(uuid1()))
        test_post.save()
        wall = self.pleb.wall.all()[0]
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        my_comment = SBComment(content='test comment', object_uuid=str(uuid1()))
        my_comment.save()
        rel_to_pleb = my_comment.is_owned_by.connect(test_user)
        rel_to_pleb.save()
        rel_from_pleb = test_user.comments.connect(my_comment)
        rel_from_pleb.save()
        rel_from_post = test_post.comments.connect(my_comment)
        rel_from_post.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)
        test_user.delete()
        test_post.delete()
        my_comment.delete()

    def test_multiple_posts(self):
        post_array = []
        wall = self.pleb.wall.all()[0]
        for item in range(0, 50):
            test_post = SBPost(content='test', object_uuid=str(uuid1()))
            test_post.save()
            test_post.posted_on_wall.connect(wall)
            wall.post.connect(test_post)
            rel = test_post.owned_by.connect(self.pleb)
            rel.save()
            rel_from_pleb = self.pleb.posts.connect(test_post)
            rel_from_pleb.save()
            post_array.append(test_post)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("profile_page",
                                           kwargs={"pleb_username":
                                                       self.pleb.username}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        for post in post_array:
            post.delete()

    def test_multiple_posts_friends(self):
        wall = self.pleb.wall.all()[0]
        pleb_array = []
        post_array = []
        for item in range(0, 2):
            test_pleb = Pleb(email=str(uuid1())[:32])
            test_pleb.save()
            pleb_array.append(test_pleb)
            for number in range(0, 10):
                test_post = SBPost(content='test', object_uuid=str(uuid1()))
                test_post.save()
                test_post.posted_on_wall.connect(wall)
                wall.post.connect(test_post)
                rel = test_post.owned_by.connect(test_pleb)
                rel.save()
                rel_from_pleb = test_pleb.posts.connect(test_post)
                rel_from_pleb.save()
                post_array.append(test_post)
        test_post = SBPost(content='test', object_uuid=str(uuid1()))
        test_post.save()
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)
        for item in pleb_array:
            item.delete()
        for post in post_array:
            post.delete()
        test_post.delete()

    def test_multiple_posts_multiple_comments_friends(self):
        wall = self.pleb.wall.all()[0]
        pleb_array = []
        post_array = []
        comment_array = []
        for item in range(0, 2):
            test_pleb = Pleb(email=str(uuid1())[:32])
            test_pleb.save()
            pleb_array.append(test_pleb)
            for number in range(0, 10):
                test_post = SBPost(content='test', object_uuid=str(uuid1()))
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
                                           object_uuid=str(uuid1()))
                    my_comment.save()
                    rel_to_pleb = my_comment.is_owned_by.connect(test_pleb)
                    rel_to_pleb.save()
                    rel_from_pleb = test_pleb.comments.connect(my_comment)
                    rel_from_pleb.save()
                    rel_from_post = test_post.comments.connect(my_comment)
                    rel_from_post.save()
                    comment_array.append(my_comment)
                    my_comment = SBComment(content='test comment',
                                           object_uuid=str(uuid1()))
                    my_comment.save()
                    rel_to_pleb = my_comment.is_owned_by.connect(self.pleb)
                    rel_to_pleb.save()
                    rel_from_pleb = self.pleb.comments.connect(my_comment)
                    rel_from_pleb.save()
                    rel_from_post = test_post.comments.connect(my_comment)
                    rel_from_post.save()
                    comment_array.append(my_comment)
        test_post = SBPost(content='test', object_uuid=str(uuid1()))
        test_post.save()
        test_post.posted_on_wall.connect(wall)
        wall.post.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)
        for item in pleb_array:
            item.delete()
        for post in post_array:
            post.delete()
        for comment in comment_array:
            comment.delete()
        test_post.delete()

    def test_pleb_does_not_exist(self):
        request = self.factory.get('/fake_username')
        request.user = self.user
        response = profile_page(request, 'fake_username')

        self.assertEqual(response.status_code, 302)



class TestProfilePageAbout(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()

    def test_profile_about_page_success(self):
        request = self.factory.get('/%s/about/' % self.pleb.username)
        request.user = self.user
        response = about_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)

    def test_profile_about_page_unauthenticated(self):
        request = self.factory.get('/%s/about/' % self.pleb.username)
        request.user = AnonymousUser()
        response = about_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 302)

    def test_pleb_does_not_exist(self):
        request = self.factory.get('/fake_username')
        request.user = self.user
        response = about_page(request, 'fake_username')

        self.assertEqual(response.status_code, 302)


class TestProfilePageReputationPage(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()

    def test_profile_reputation_page_success(self):
        request = self.factory.get('/%s/reputation/' % self.pleb.username)
        request.user = self.user
        response = reputation_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)

    def test_profile_reputation_page_unauthenticated(self):
        request = self.factory.get('/%s/reputation/' % self.pleb.username)
        request.user = AnonymousUser()
        response = reputation_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 302)

    def test_pleb_does_not_exist(self):
        request = self.factory.get('/fake_username')
        request.user = self.user
        response = reputation_page(request, 'fake_username')

        self.assertEqual(response.status_code, 302)

class TestProfilePageFriendPage(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()

    def test_profile_friend_page_success(self):
        request = self.factory.get('/%s/friends/' % self.pleb.username)
        request.user = self.user
        response = friends_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 200)

    def test_profile_friend_page_unauthenticated(self):
        request = self.factory.get('/%s/friends/' % self.pleb.username)
        request.user = AnonymousUser()
        response = friends_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 302)

    def test_pleb_does_not_exist(self):
        request = self.factory.get('/fake_username')
        request.user = self.user
        response = friends_page(request, 'fake_username')

        self.assertEqual(response.status_code, 302)
