from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import UniqueProperty

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from sb_registration.utils import create_user_util_test


class TagEndpointTest(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        try:
            self.tag = Tag(name='test_tag').save()
        except UniqueProperty:
            self.tag = Tag.nodes.get(name='test_tag')
        try:
            self.base_tag = Tag(name='test_base_tag', base=True).save()
        except UniqueProperty:
            self.base_tag = Tag.nodes.get(name='test_base_tag')

    def test_list_unauthorized(self):
        url = reverse('tag-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_unauthorized(self):
        url = reverse('tag-detail',
                      kwargs={"name": self.tag.name})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-detail',
                      kwargs={"name": self.tag.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            "id": response.data['id'],
            "type": "tag",
            "name": self.tag.name,
            "href": response.data['href']
        }, response.data)
        self.assertIn('http', response.data['href'])

    def test_update_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-detail',
                      kwargs={"name": self.tag.name})
        response = self.client.put(url, data={'name': 'name_change'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

    def test_suggestion_engine(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-suggestion-engine') + "?page_size=500"
        response = self.client.get(url)
        self.assertIn({"value": "test_tag"}, response.data['results'])
        self.assertIn({"value": "test_base_tag"}, response.data['results'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suggestion_engine_exclude_base(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-suggestion-engine') + "?exclude_base=true"
        response = self.client.get(url)
        self.assertNotIn([{"value": "test_base_tag"}],
                         response.data['results'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
