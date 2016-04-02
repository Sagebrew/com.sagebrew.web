from uuid import uuid1

from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.cache import cache

from sb_comments.neo_models import Comment
from sb_posts.neo_models import Post
from sb_registration.utils import create_user_util_test
from api.utils import wait_util

from plebs.neo_models import Pleb, FriendRequest
from plebs.views import ProfileView


class ProfilePageTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()

    def test_unauthenticated(self):
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = AnonymousUser()
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_without_post(self):
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [status.HTTP_200_OK,
                                             status.HTTP_302_FOUND])

    def test_with_post(self):
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        wall = self.pleb.get_wall()
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        test_post.owned_by.connect(self.pleb)
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [status.HTTP_200_OK,
                                             status.HTTP_302_FOUND])
        test_post.delete()

    def test_post_with_comments(self):
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        wall = self.pleb.get_wall()
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        test_post.owned_by.connect(self.pleb)
        my_comment = Comment(content='test comment', object_uuid=str(uuid1()),
                             owner_username=self.pleb.username)
        my_comment.save()
        my_comment.owned_by.connect(self.pleb)
        test_post.comments.connect(my_comment)
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [status.HTTP_200_OK,
                                             status.HTTP_302_FOUND])
        test_post.delete()
        my_comment.delete()

    def test_post_with_comments_from_friend(self):
        test_user = Pleb(email=str(uuid1()) + '@gmail.com',
                         username=str(uuid1())[:32])
        test_user.save()
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        wall = self.pleb.wall.all()[0]
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        test_post.owned_by.connect(self.pleb)
        my_comment = Comment(content='test comment', object_uuid=str(uuid1()),
                             owner_username=self.pleb.username)
        my_comment.save()
        my_comment.owned_by.connect(test_user)
        test_post.comments.connect(my_comment)
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [status.HTTP_200_OK,
                                             status.HTTP_302_FOUND])
        test_user.delete()
        test_post.delete()
        my_comment.delete()

    def test_with_friend_request(self):
        email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(email2)
        pleb2 = Pleb.nodes.get(email=email2)
        self.friend_request = FriendRequest().save()
        self.pleb.friend_requests_received.connect(self.friend_request)
        self.pleb.friend_requests_sent.connect(self.friend_request)
        self.friend_request.request_to.connect(self.pleb)
        self.friend_request.request_from.connect(pleb2)
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [200, 302])

    def test_multiple_posts(self):
        post_array = []
        wall = self.pleb.get_wall()
        for item in range(0, 50):
            test_post = Post(content='test', object_uuid=str(uuid1()),
                             owner_username=self.pleb.username,
                             wall_owner_username=self.pleb.username)
            test_post.save()
            test_post.posted_on_wall.connect(wall)
            wall.posts.connect(test_post)
            test_post.owned_by.connect(self.pleb)
            post_array.append(test_post)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("profile_page",
                                           kwargs={
                                               "pleb_username":
                                                   self.pleb.username}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        for post in post_array:
            post.delete()

    def test_multiple_posts_friends(self):
        wall = self.pleb.get_wall()
        pleb_array = []
        post_array = []
        for item in range(0, 2):
            test_pleb = Pleb(email=str(uuid1())[:32],
                             username=str(uuid1())[:32])
            test_pleb.save()
            pleb_array.append(test_pleb)
            for number in range(0, 10):
                test_post = Post(content='test', object_uuid=str(uuid1()),
                                 owner_username=self.pleb.username,
                                 wall_owner_username=self.pleb.username)
                test_post.save()
                test_post.posted_on_wall.connect(wall)
                wall.posts.connect(test_post)
                test_post.owned_by.connect(test_pleb)
                post_array.append(test_post)
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        test_post.owned_by.connect(self.pleb)
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [status.HTTP_200_OK,
                                             status.HTTP_302_FOUND])
        for item in pleb_array:
            item.delete()
        for post in post_array:
            post.delete()
        test_post.delete()

    def test_multiple_posts_multiple_comments_friends(self):
        wall = self.pleb.get_wall()
        pleb_array = []
        post_array = []
        comment_array = []
        for item in range(0, 2):
            test_pleb = Pleb(email=str(uuid1())[:32],
                             username=str(uuid1())[:32])
            test_pleb.save()
            pleb_array.append(test_pleb)
            for number in range(0, 10):
                test_post = Post(content='test', object_uuid=str(uuid1()),
                                 owner_username=self.pleb.username,
                                 wall_owner_username=self.pleb.username)
                test_post.save()
                test_post.posted_on_wall.connect(wall)
                wall.posts.connect(test_post)
                test_post.owned_by.connect(test_pleb)
                post_array.append(test_post)
                for num in range(0, 1):
                    my_comment = Comment(content='test comment',
                                         object_uuid=str(uuid1()),
                                         owner_username=self.pleb.username)
                    my_comment.save()
                    my_comment.owned_by.connect(test_pleb)
                    test_post.comments.connect(my_comment)
                    comment_array.append(my_comment)
                    my_comment = Comment(content='test comment',
                                         object_uuid=str(uuid1()),
                                         owner_username=self.pleb.username)
                    my_comment.save()
                    my_comment.owned_by.connect(self.pleb)
                    test_post.comments.connect(my_comment)
                    comment_array.append(my_comment)
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        test_post.owned_by.connect(self.pleb)
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [status.HTTP_200_OK,
                                             status.HTTP_302_FOUND])
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
        profile_page = ProfileView.as_view()
        response = profile_page(request, 'fake_username')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)


class TestSettingPages(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = Client()
        self.email = "success@simulator.amazonses.com"
        self.password = "test_test"
        res = create_user_util_test(self.email, password=self.password,
                                    task=True)
        wait_util(res)
        self.assertNotEqual(res, False)
        self.username = res["username"]
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()
        cache.clear()

    def test_settings_page(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse("general_settings")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_settings_no_quest(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse("general_settings")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contribute(self):
        cache.set(self.pleb.username, self.pleb)
        self.client.login(username=self.user.username, password=self.password)
        url = reverse("contribute_settings")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
