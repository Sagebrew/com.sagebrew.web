import time
from uuid import uuid1
from datetime import datetime
from dateutil import parser

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.response import TemplateResponse

from neomodel import UniqueProperty, db

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_posts.neo_models import Post
from sb_uploads.neo_models import UploadedObject, URLContent
from sb_registration.utils import create_user_util_test


class PostsEndpointTests(APITestCase):

    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounces@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.user2 = User.objects.get(email=self.email2)
        self.post = Post(content="Hey I'm a post",
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username).save()
        self.post.owned_by.connect(self.pleb)
        self.post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(self.post)
        self.user = User.objects.get(email=self.email)

    def test_unauthorized(self):
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        data = None
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual("Hey I'm a post", response.data['content'])

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['profile'],
                         "test_test")

    def test_view_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['view_count'], 0)

    def test_object_uuid(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['object_uuid'], self.post.object_uuid)

    def test_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['id'], self.post.object_uuid)

    def test_last_edited_on(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertIsInstance(parser.parse(response.data['last_edited_on']),
                              datetime)

    def test_created(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertIsInstance(parser.parse(response.data['created']),
                              datetime)

    def test_vote_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['vote_type'])

    def test_downvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['downvotes'], 0)

    def test_upvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, follow=True, format='json')
        self.assertEqual(response.data['upvotes'], 0)

    def test_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['url'],
                         "http://testserver/user/test_test/")

    def test_vote_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['vote_count'], 0)

    def test_flagged_by(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['flagged_by'], [])

    def test_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['href'],
                         'http://testserver/v1/posts/%s/' % (
                             self.post.object_uuid))

    def test_wall_owner_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['wall_owner_profile'],
                         'http://testserver/v1/profiles/test_test/')

    def test_read_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['type'], 'post')

    def test_not_owner(self):
        other_email = "bounce@simulator.amazonses.com"
        create_user_util_test(other_email)
        other_user = User.objects.get(email=other_email)
        self.client.force_authenticate(user=other_user)

        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_update_status(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "content": "Hey it's a new post"
        }
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_owner_update(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            "content": "Hey it's a new post"
        }
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Only the owner can edit this'])
        self.assertEqual(
            Post.nodes.get(object_uuid=self.post.object_uuid).content,
            self.post.content)

    def test_owner_update_detail(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "content": "Hey it's a new post yo"
        }
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['content'], "Hey it's a new post yo")

    def test_owner_update_db(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "content": "Hey it's a new post db"
        }
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        self.client.put(url, data, format='json')
        self.assertEqual(
            Post.nodes.get(object_uuid=self.post.object_uuid).content,
            "Hey it's a new post db")

    def test_not_owner_but_admin(self):
        other_email = "bounce@simulator.amazonses.com"
        create_user_util_test(other_email)
        other_user = User.objects.get(email=other_email)
        other_user.is_staff = True
        other_user.is_superuser = True
        other_user.save()
        self.client.force_authenticate(user=other_user)

        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        post = Post(content='This is a test post',
                    wall_owner_username=self.pleb.username).save()
        url = reverse("post-detail",
                      kwargs={"object_uuid": post.object_uuid})
        url_content = URLContent(url="http://reddit.com").save()
        self.client.patch(
            url, data={"content": "This is a test post reddit.com",
                       "included_urls": ["http://reddit.com"]}, format='json')
        self.assertTrue(post.url_content.is_connected(url_content))
        url_content.delete()


class PostListCreateTest(APITestCase):

    def setUp(self):
        self.unit_under_test_name = 'post'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_unauthorized(self):
        url = reverse('post-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_own_wall(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        data = {
            "content": "hey I made a post!"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['content'], data['content'])

    def test_create_with_uploaded_object(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        uploaded_object = UploadedObject().save()
        data = {
            "content": "hey I made a post!",
            "images": [uploaded_object.object_uuid]
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uploaded_objects'][0]['id'],
                         uploaded_object.object_uuid)

    def test_create_with_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        try:
            url_content = URLContent(url="example.com").save()
        except UniqueProperty:
            url_content = URLContent.nodes.get(url="example.com")
        data = {
            "content": "hey I made a post!",
            "included_urls": ["example.com"]
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['url_content'][0]['id'],
                         url_content.object_uuid)

    def test_create_with_url_does_not_exist(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        data = {
            "content": "hey I made a post!",
            "included_urls": ["www.example.com"]
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_on_friends_wall(self):
        self.client.force_authenticate(user=self.user)
        email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(email2, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        friend = Pleb.nodes.get(email=email2)
        self.pleb.friends.connect(friend)
        friend.friends.connect(self.pleb)
        url = reverse('post-list')
        data = {
            "content": "hey I made a post!",
            "wall": friend.username
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['content'], data['content'])

    def test_create_on_non_friends_wall(self):
        self.client.force_authenticate(user=self.user)
        email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(email2, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        friend = Pleb.nodes.get(email=email2)
        self.pleb.friends.disconnect(friend)
        friend.friends.disconnect(self.pleb)
        url = reverse('post-list')
        data = {
            "content": "hey I made a post!",
            "wall": friend.username
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], "Sorry you are not friends "
                                                  "with this person.")

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['content'][
                         0], 'This field is required.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list')
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        self.client.force_authenticate(user=self.user)
        query = 'MATCH (a:Post) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        url = reverse('post-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 0)

    def test_list_with_items(self):
        self.client.force_authenticate(user=self.user)
        post = Post(content="My first post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        wall = self.pleb.get_wall()
        wall.posts.connect(post)
        post.posted_on_wall.connect(wall)
        url = reverse('post-list')
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)

    def test_list_with_items_not_friends(self):
        self.client.force_authenticate(user=self.user)
        email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(email2, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        friend = Pleb.nodes.get(email=email2)
        post = Post(content="My first post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        wall = friend.get_wall()
        wall.posts.connect(post)
        post.posted_on_wall.connect(wall)
        self.pleb.friends.disconnect(friend)
        friend.friends.disconnect(self.pleb)
        url = "%s?wall=%s" % (reverse('post-list'), friend.username)
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'], [])

    def test_list_with_items_friends(self):
        self.client.force_authenticate(user=self.user)
        email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(email2, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        friend = Pleb.nodes.get(email=email2)
        post = Post(content="My first post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        wall = friend.get_wall()
        wall.posts.connect(post)
        post.posted_on_wall.connect(wall)
        self.pleb.friends.connect(friend)
        friend.friends.connect(self.pleb)
        url = "%s?wall=%s" % (reverse('post-list'), friend.username)
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)


class TestSinglePostPage(APITestCase):

    def setUp(self):
        self.unit_under_test_name = 'post'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.post = Post(content="some dummy content").save()

    def test_get_single_page(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('single_post_page',
                      kwargs={'object_uuid': self.post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, TemplateResponse)


class WallPostListCreateTest(APITestCase):

    def setUp(self):
        from sb_wall.neo_models import Wall
        query = 'MATCH (a) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        cache.clear()
        self.unit_under_test_name = 'post'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        query = 'MATCH (pleb:Pleb {username: "%s"})' \
                '-[:OWNS_WALL]->(wall:Wall) ' \
                'RETURN wall' % self.pleb.username
        res, _ = db.cypher_query(query)
        if res.one is None:
            wall = Wall(wall_id=str(uuid1())).save()
            query = 'MATCH (pleb:Pleb {username: "%s"}),' \
                    '(wall:Wall {wall_id: "%s"}) ' \
                    'CREATE UNIQUE (pleb)-[:OWNS_WALL]->(wall) ' \
                    'RETURN wall' % (self.pleb.username, wall.wall_id)
            res, _ = db.cypher_query(query)
        self.wall = Wall.inflate(res.one)

    def test_unauthorized(self):
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['content'][
                         0], 'This field is required.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        self.client.force_authenticate(user=self.user)
        query = 'MATCH (a:Post) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 0)

    def test_list_with_items(self):
        self.client.force_authenticate(user=self.user)
        post = Post(content="My first post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        self.wall.posts.connect(post)
        post.posted_on_wall.connect(self.wall)
        url = reverse('profile-wall', kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)

    def test_list_with_items_not_friends(self):
        self.client.force_authenticate(user=self.user)
        email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(email2, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        friend = Pleb.nodes.get(email=email2)
        post = Post(content="My first post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        wall = friend.get_wall()
        wall.posts.connect(post)
        post.posted_on_wall.connect(wall)
        self.pleb.friends.disconnect(friend)
        friend.friends.disconnect(self.pleb)
        url = reverse('profile-wall', kwargs={'username': friend.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'], [])

    def test_list_with_items_friends(self):
        from sb_wall.neo_models import Wall
        self.client.force_authenticate(user=self.user)
        email2 = "bounce@simulator.amazonses.com"
        friend = create_user_util_test(email2)
        query = 'MATCH (pleb:Pleb {username: "%s"})' \
                '-[:OWNS_WALL]->(wall:Wall) ' \
                'RETURN wall' % friend.username
        res, _ = db.cypher_query(query)
        if res.one is None:
            wall = Wall(wall_id=str(uuid1())).save()
            query = 'MATCH (pleb:Pleb {username: "%s"}),' \
                    '(wall:Wall {wall_id: "%s"}) ' \
                    'CREATE UNIQUE (pleb)-[:OWNS_WALL]->(wall) ' \
                    'RETURN wall' % (friend.username, wall.wall_id)
            res, _ = db.cypher_query(query)
        wall = Wall.inflate(res.one)
        post = Post(content="My first post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        wall.posts.connect(post)
        post.posted_on_wall.connect(wall)
        self.pleb.friends.connect(friend)
        friend.friends.connect(self.pleb)
        url = reverse('profile-wall', kwargs={'username': friend.username})
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-wall',
                      kwargs={'username': self.pleb.username}) + "?html=true"
        response = self.client.post(
            url, data={'content': 'this is a test content thing'},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
