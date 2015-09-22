import requests_mock

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_posts.neo_models import Post
from sb_comments.neo_models import Comment
from sb_registration.utils import create_user_util_test


class TestCommentsRetrieveUpdateDestroy(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'comment'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.post = Post(content='test content',
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username).save()
        self.post.owned_by.connect(self.pleb)
        self.comment = Comment(content="test comment",
                               owner_username=self.pleb.username).save()
        self.comment.owned_by.connect(self.pleb)
        self.comment.comment_on.connect(self.post)
        self.post.comments.connect(self.comment)

    def test_unauthorized(self):
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        data = {'missing': 'test missing data'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detail_unauthorized(self):
        url = reverse('comment-detail',
                      kwargs={'object_uuid': self.comment.object_uuid})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_list_render(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid}) + \
            "comments/render/?expedite=true&expand=true&" \
            "html=true&page_size=3"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_render_html_key(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid}) + \
            "comments/render/?expedite=true&" \
            "expand=true&html=true&page_size=3"
        response = self.client.get(url)
        self.assertIn('html', response.data['results'])
        self.assertNotEqual([], response.data['results']['html'])

    def test_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertEqual(response.data['detail'],
                         "We do not allow users to query all the comments on "
                         "the site.")
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

    def test_private_content_with_comment_unauthorized(self):
        post = Post(content='test_content',
                    owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        self.pleb.posts.connect(post)
        comment = Comment(content="This is my new comment").save()
        post.comments.connect(comment)
        comment.comment_on.connect(post)
        url = "%scomments/?expand=true" % reverse(
            'post-detail',
            kwargs={"object_uuid": post.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        comment = Comment(url='this is a url',
                          content='this is content').save()
        parent = Post(content='some content').save()
        comment.comment_on.connect(parent)
        url = reverse("comment-detail",
                      kwargs={'comment_uuid': comment.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestCommentListCreate(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'comment'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.post = Post(content='test content',
                         owner_username=self.pleb.username,
                         wall_owner_username=self.pleb.username).save()
        self.post.owned_by.connect(self.pleb)
        self.comment = Comment(content="test comment",
                               owner_username=self.pleb.username).save()
        self.comment.owned_by.connect(self.pleb)
        self.comment.comment_on.connect(self.post)
        self.post.comments.connect(self.comment)
        self.api_endpoint = "http://testserver/v1"

    @requests_mock.mock()
    def test_create(self, m):
        self.client.force_authenticate(user=self.user)
        m.get("%s/posts/%s/" % (self.api_endpoint, self.post.object_uuid),
              json={
                  "url": "http://www.sagebrew.com/v1/posts/%s/" %
                         self.post.object_uuid},
              status_code=status.HTTP_200_OK)
        url = reverse('post-detail',
                      kwargs={"object_uuid":
                              self.post.object_uuid}) + "comments/"
        response = self.client.post(
            url, data={'content': "this is my test comment content"},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @requests_mock.mock()
    def test_create_html(self, m):
        self.client.force_authenticate(user=self.user)
        m.get("%s/posts/%s/" % (self.api_endpoint, self.post.object_uuid),
              json={"url":
                    "http://www.sagebrew.com/v1/posts/%s/" %
                    self.post.object_uuid},
              status_code=status.HTTP_200_OK)
        url = reverse(
            'post-detail', kwargs={"object_uuid": self.post.object_uuid}) + \
            "comments/?html=true"
        response = self.client.post(
            url, data={'content': "this is my test comment content"},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
