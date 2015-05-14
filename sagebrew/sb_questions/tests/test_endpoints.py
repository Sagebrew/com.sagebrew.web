import time
from dateutil import parser

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase


from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test


class QuestionEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.question = Question(content="Hey I'm a question",
                                 title="test question title").save()
        self.pleb = Pleb.nodes.get(email=self.email)
        self.question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(self.question)
        self.user = User.objects.get(email=self.email)

    def test_unauthorized(self):
        url = reverse('question-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN,
                                             status.HTTP_401_UNAUTHORIZED])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response_data, response.data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        data = None
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.content, response.data['content'])

    def test_get_title(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.title, response.data['title'])

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('http://testserver/v1/profiles/test_test/',
                         response.data['profile'])

    def test_get_view_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['view_count'])

    def test_get_object_uuid(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.object_uuid,
                         response.data['object_uuid'])

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.object_uuid, response.data['id'])

    def test_last_edited_on(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.last_edited_on,
                         parser.parse(response.data['last_edited_on']))

    def test_get_created(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.created,
                         parser.parse(response.data['created']))

    def test_get_vote_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(None, response.data['vote_type'])

    def test_get_downvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['downvotes'])

    def test_get_upvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['upvotes'])

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/conversations/%s/"%
                         (self.question.object_uuid), response.data['url'])

    def test_get_vote_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['vote_count'])

    def test_get_flagged_by(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['flagged_by'])

    def test_get_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/v1/questions/%s/"%
                         (self.question.object_uuid), response.data['href'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('question', response.data['type'])

    def test_get_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, len(response.data))
        self.assertEqual(1, len(response.data['results']))

    def test_list_tagged_as(self):
        tag = Tag(name='fiscal').save()
        self.question.tags.connect(tag)
        self.client.force_authenticate(user=self.user)
        url = reverse('question-list')+"?limit=5&offset=0&" \
                                       "expand=true&tagged_as=fiscal"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['tags'][0], 'fiscal')

    def test_list_most_recent(self):
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content').save()
        question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(question)
        url = reverse('question-list')+"?limit=5&offset=0&" \
                                       "expand=true&sort_by=-created"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_least_recent(self):
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content').save()
        question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(question)
        url = reverse('question-list')+"?limit=5&offset=0&" \
                                       "expand=true&sort_by=created"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
