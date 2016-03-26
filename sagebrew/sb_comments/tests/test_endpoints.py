from uuid import uuid1
import requests_mock

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import DoesNotExist, db

from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_privileges.neo_models import Privilege
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
        comment = Comment(content="This is my new comment").save()
        post.comments.connect(comment)
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
        parent.comments.connect(comment)
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


class SBBaseSerializerCommentTests(APITestCase):
    # TODO This should be moved somewhere not tighly coupled to a give content
    # object.
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounces@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.title = str(uuid1())
        self.question = Question(content="Hey I'm a question",
                                 title=self.title,
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)
        self.user = User.objects.get(email=self.email)
        try:
            Privilege.nodes.get(name="flag")
        except(Privilege.DoesNotExist, DoesNotExist):
            call_command('create_privileges')

    @requests_mock.mock()
    def test_can_flag(self, m):
        m.get(
            reverse('question-detail',
                    kwargs={'object_uuid': self.question.object_uuid}),
            json=QuestionSerializerNeo(self.question).data,
            status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        comment = Comment(content='test_content',
                          owner_username=self.pleb2.username,
                          parent_type="question",
                          parent_id=self.question.object_uuid).save()
        comment.owned_by.connect(self.pleb2)
        self.question.comments.connect(comment)
        privilege = Privilege.nodes.get(name="flag")
        self.pleb.privileges.connect(privilege)
        cache.clear()
        url = "%scomments/%s/?expedite=true" % (
            reverse('question-detail',
                    kwargs={'object_uuid': self.question.object_uuid}),
            comment.object_uuid)
        response = self.client.get(url, format='json')
        self.pleb.privileges.disconnect(privilege)
        self.question.comments.disconnect(comment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_flag']['status'])
        self.assertIsNone(response.data['can_flag']['detail'])
        self.assertIsNone(response.data['can_flag']['short_detail'])

    @requests_mock.mock()
    def test_login_to_flag(self, m):
        m.get(
            reverse('question-detail',
                    kwargs={'object_uuid': self.question.object_uuid}),
            json=QuestionSerializerNeo(self.question).data,
            status_code=status.HTTP_200_OK)
        comment = Comment(content='test_content',
                          owner_username=self.pleb.username,
                          parent_type="question",
                          parent_id=self.question.object_uuid,
                          visibility="public").save()
        comment.owned_by.connect(self.pleb)
        self.question.comments.connect(comment)
        url = "%scomments/%s/" % (
            reverse('question-detail',
                    kwargs={'object_uuid': self.question.object_uuid}),
            comment.object_uuid)
        response = self.client.get(url, format='json')
        self.question.comments.disconnect(comment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_flag']['status'])
        self.assertEqual(response.data['can_flag']['detail'],
                         "You must be logged in to flag content.")
        self.assertEqual(response.data['can_flag']['short_detail'],
                         "Signup To Flag")

    @requests_mock.mock()
    def test_can_not_flag(self, m):
        m.get(
            reverse('question-detail',
                    kwargs={'object_uuid': self.question.object_uuid}),
            json=QuestionSerializerNeo(self.question).data,
            status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        comment = Comment(content='test_content',
                          owner_username=self.pleb2.username,
                          parent_type="question",
                          parent_id=self.question.object_uuid).save()
        comment.owned_by.connect(self.pleb2)
        self.question.comments.connect(comment)
        self.pleb.save()
        for item in self.pleb.privileges.all():
            self.pleb.privileges.disconnect(item)
        cache.clear()
        url = "%scomments/%s/" % (
            reverse('question-detail',
                    kwargs={'object_uuid': self.question.object_uuid}),
            comment.object_uuid)
        response = self.client.get(url, format='json')
        self.question.comments.disconnect(comment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_flag']['status'])
        self.assertEqual(response.data['can_flag']['detail'],
                         "You must have 50+ reputation to flag Conversation "
                         "Cloud content.")
        self.assertEqual(response.data['can_flag']['short_detail'],
                         "Requirement: 50+ Reputation")

    @requests_mock.mock()
    def test_can_not_flag_own(self, m):
        m.get(
            reverse('question-detail',
                    kwargs={'object_uuid': self.question.object_uuid}),
            json=QuestionSerializerNeo(self.question).data,
            status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        comment = Comment(content='test_content',
                          owner_username=self.pleb.username,
                          parent_type="question",
                          parent_id=self.question.object_uuid).save()
        comment.owned_by.connect(self.pleb)
        self.question.comments.connect(comment)
        url = "%scomments/%s/" % (
            reverse('question-detail',
                    kwargs={'object_uuid': self.question.object_uuid}),
            comment.object_uuid)
        response = self.client.get(url, format='json')
        self.question.comments.disconnect(comment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_flag']['status'])
        self.assertEqual(response.data['can_flag']['detail'],
                         "You cannot flag your own content")
        self.assertEqual(response.data['can_flag']['short_detail'],
                         "Cannot Flag Own Content")