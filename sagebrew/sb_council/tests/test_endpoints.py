from uuid import uuid1
import time
from dateutil import parser

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test
from sb_flags.neo_models import Flag


class CouncilEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'sbcontent'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.flag = Flag().save()
        self.question = Question(owner_username=self.pleb.username,
                                 title=str(uuid1())).save()
        self.question.flags.connect(self.flag)
        self.question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(self.question)

    def test_unauthorized(self):
        url = reverse('council-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_list_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_filter(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list') + "?filter=voted"
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_html(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list') + "?html=true&filter="
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_with_object(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['profile'], self.pleb.username)

    def test_get_viewcount(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['view_count'], 0)

    def test_get_object_uuid(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['object_uuid'],
                         self.question.object_uuid)

    def test_get_last_edited_on(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(parser.parse(response.data['last_edited_on']),
                         self.question.last_edited_on)

    def test_get_created(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(parser.parse(response.data['created']),
                         self.question.created)

    def test_get_council_vote(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['council_vote'])

    def test_get_downvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['downvotes'], 0)

    def test_get_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['content'])

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['url'])

    def test_get_vote_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['vote_count'], 0)

    def test_get_flagged_by(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['flagged_by'], [])

    def test_get_upvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['upvotes'], 0)

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['type'], 'sbcontent')

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['id'], self.question.object_uuid)

    def test_get_is_closed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})

        response = self.client.get(url, format='json')
        self.assertFalse(response.data['is_closed'])

    def test_create_vote(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.put(url, data={'vote_type': True},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['council_vote'])

    def test_create_council_vote_down(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.put(url, data={'vote_type': False},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['council_vote'])

    def test_get_after_vote(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        self.client.put(url, data={'vote_type': True}, format='json')
        time.sleep(10)  # allow for task to finish
        get_response = self.client.get(url, format='json')
        self.assertTrue(get_response.data['is_closed'])
