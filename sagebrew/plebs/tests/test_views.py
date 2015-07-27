from uuid import uuid1
from base64 import b64encode
from json import loads

from rest_framework import status
from rest_framework.test import APIRequestFactory

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings

from sb_comments.neo_models import Comment
from sb_posts.neo_models import Post
from plebs.neo_models import Pleb, FriendRequest
from plebs.views import (ProfileView, create_friend_request)
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
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertEqual(response.status_code, 302)

    def test_without_post(self):
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [200, 302])

    def test_with_post(self):
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        wall = self.pleb.get_wall()
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [200, 302])
        test_post.delete()

    def test_post_with_comments(self):
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        wall = self.pleb.get_wall()
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        my_comment = Comment(content='test comment', object_uuid=str(uuid1()),
                             owner_username=self.pleb.username)
        my_comment.save()
        rel_to_pleb = my_comment.owned_by.connect(self.pleb)
        rel_to_pleb.save()
        rel_from_pleb = self.pleb.comments.connect(my_comment)
        rel_from_pleb.save()
        rel_from_post = test_post.comments.connect(my_comment)
        rel_from_post.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [200, 302])
        test_post.delete()
        my_comment.delete()

    def test_post_with_comments_from_friend(self):
        test_user = Pleb(email=str(uuid1()) + '@gmail.com')
        test_user.save()
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        wall = self.pleb.wall.all()[0]
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        my_comment = Comment(content='test comment', object_uuid=str(uuid1()),
                             owner_username=self.pleb.username)
        my_comment.save()
        rel_to_pleb = my_comment.owned_by.connect(test_user)
        rel_to_pleb.save()
        rel_from_pleb = test_user.comments.connect(my_comment)
        rel_from_pleb.save()
        rel_from_post = test_post.comments.connect(my_comment)
        rel_from_post.save()
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
            rel = test_post.owned_by.connect(self.pleb)
            rel.save()
            rel_from_pleb = self.pleb.posts.connect(test_post)
            rel_from_pleb.save()
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
            test_pleb = Pleb(email=str(uuid1())[:32])
            test_pleb.save()
            pleb_array.append(test_pleb)
            for number in range(0, 10):
                test_post = Post(content='test', object_uuid=str(uuid1()),
                                 owner_username=self.pleb.username,
                                 wall_owner_username=self.pleb.username)
                test_post.save()
                test_post.posted_on_wall.connect(wall)
                wall.posts.connect(test_post)
                rel = test_post.owned_by.connect(test_pleb)
                rel.save()
                rel_from_pleb = test_pleb.posts.connect(test_post)
                rel_from_pleb.save()
                post_array.append(test_post)
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [302, 200])
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
            test_pleb = Pleb(email=str(uuid1())[:32])
            test_pleb.save()
            pleb_array.append(test_pleb)
            for number in range(0, 10):
                test_post = Post(content='test', object_uuid=str(uuid1()),
                                 owner_username=self.pleb.username,
                                 wall_owner_username=self.pleb.username)
                test_post.save()
                test_post.posted_on_wall.connect(wall)
                wall.posts.connect(test_post)
                rel = test_post.owned_by.connect(test_pleb)
                rel.save()
                rel_from_pleb = test_pleb.posts.connect(test_post)
                rel_from_pleb.save()
                post_array.append(test_post)
                for num in range(0, 1):
                    my_comment = Comment(content='test comment',
                                         object_uuid=str(uuid1()),
                                         owner_username=self.pleb.username)
                    my_comment.save()
                    rel_to_pleb = my_comment.owned_by.connect(test_pleb)
                    rel_to_pleb.save()
                    rel_from_pleb = test_pleb.comments.connect(my_comment)
                    rel_from_pleb.save()
                    rel_from_post = test_post.comments.connect(my_comment)
                    rel_from_post.save()
                    comment_array.append(my_comment)
                    my_comment = Comment(content='test comment',
                                         object_uuid=str(uuid1()),
                                         owner_username=self.pleb.username)
                    my_comment.save()
                    rel_to_pleb = my_comment.owned_by.connect(self.pleb)
                    rel_to_pleb.save()
                    rel_from_pleb = self.pleb.comments.connect(my_comment)
                    rel_from_pleb.save()
                    rel_from_post = test_post.comments.connect(my_comment)
                    rel_from_post.save()
                    comment_array.append(my_comment)
        test_post = Post(content='test', object_uuid=str(uuid1()),
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username)
        test_post.save()
        test_post.posted_on_wall.connect(wall)
        wall.posts.connect(test_post)
        rel = test_post.owned_by.connect(self.pleb)
        rel.save()
        rel_from_pleb = self.pleb.posts.connect(test_post)
        rel_from_pleb.save()
        request = self.factory.get('/%s' % self.pleb.username)
        request.user = self.user
        profile_page = ProfileView.as_view()
        response = profile_page(request, self.pleb.username)
        self.assertIn(response.status_code, [200, 302])
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

        self.assertEqual(response.status_code, 302)


class TestCreateFriendRequestView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_create_friend_request_view_success(self):
        data = {
            'from_username': self.user.username,
            'to_username': self.user2.username,
        }
        request = self.factory.post('/relationships/create_friend_request',
                                    data=data, format='json')
        request.user = self.user

        res = create_friend_request(request)

        res.render()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(loads(res.content)['action'])

    def test_create_friend_request_view_invalid_form(self):
        data = {
            'from_username': self.user.username,
            'totallyincorrectform': self.user2.username,
            'object_uuid': ''
        }
        request = self.factory.post('/relationships/create_friend_request',
                                    data=data, format='json')
        request.user = self.user

        res = create_friend_request(request)

        res.render()

        self.assertEqual(res.status_code, 400)
        self.assertEqual(loads(res.content)['detail'], 'invalid form')

    def test_create_friend_request_view_incorrect_data_int(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data=1123123, format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_string(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data='1123123', format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_float(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data=11.23123, format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_list(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data=[], format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_dict(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data={}, format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_image(self):
        with open("%s/sb_posts/tests/images/test_image.jpg" % (
                settings.PROJECT_DIR), "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/relationships/create_friend_request',
                                    data=image, format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)
