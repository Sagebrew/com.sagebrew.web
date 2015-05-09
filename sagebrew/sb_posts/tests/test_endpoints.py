import time
from datetime import datetime
from dateutil import parser

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_posts.neo_models import Post
from sb_registration.utils import create_user_util_test


class PostsEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(1)
        self.post = Post(content="Hey I'm a post").save()
        self.pleb = Pleb.nodes.get(email=self.email)
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
                         "http://testserver/v1/profiles/test_test/")

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
        response = self.client.get(url, format='json')
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
