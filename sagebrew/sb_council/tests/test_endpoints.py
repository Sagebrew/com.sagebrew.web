from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from django.templatetags import static

from neomodel import db
from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test
from sb_flags.neo_models import Flag
from sb_posts.neo_models import Post
from sb_solutions.neo_models import Solution


class CouncilEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'sbcontent'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

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

    def test_list_with_object(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('council-list')
        flag = Flag().save()
        question = Question().save()
        question.flags.connect(flag)
        res, _ = db.cypher_query('MATCH (q:Question)-[:HAS_FLAG]->(f:Flag) RETURN q')
        print res
        response = self.client.get(url, format='json')
        print response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
