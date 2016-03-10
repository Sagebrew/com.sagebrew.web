from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify

from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import UniqueProperty

from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from sb_registration.utils import create_user_util_test


class TagEndpointTest(APITestCase):

    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        try:
            self.tag = Tag(name='test_tag',
                           owner_username=self.pleb.username).save()
        except UniqueProperty:
            self.tag = Tag.nodes.get(name='test_tag')
        try:
            self.base_tag = Tag(name='test_base_tag', base=True,
                                owner_username=self.pleb.username).save()
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
        self.assertEqual(response.data['id'], self.tag.object_uuid)
        self.assertIn('http', response.data['href'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-detail',
                      kwargs={"name": self.tag.name})
        response = self.client.get(url)
        self.assertEqual(response.data['type'], "tag")

    def test_get_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-detail',
                      kwargs={"name": self.tag.name})
        response = self.client.get(url)
        self.assertEqual(response.data['name'], self.tag.name)

    def test_update_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-detail',
                      kwargs={"name": self.tag.name})
        response = self.client.put(url, data={'name': 'name_change'},
                                   format='json')
        # This throws a 403 because currently you must be an admin or the
        # endpoint is read only. So by trying to update it as a normal user
        # it throws a 403 prior to getting into the view and throwing a
        # 501
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_get_non_url_friendly(self):
        name = ' !@#$%^&*()_+~`1234567890-=[]\{}|;:",./<>?qwer  lsls., '
        tag2 = Tag(
            name=name,
            owner_username=self.pleb.username).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-detail',
                      kwargs={"name": slugify(tag2.name)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], slugify(name))

    def test_list_non_url_friendly(self):
        name = ' 112@#$%^&*()_+~`1234567890-=[]\{}|;:",./<>?qwer  lsls., '
        tag2 = Tag(
            name=name,
            owner_username=self.pleb.username).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('tag-detail',
                      kwargs={"name": slugify(tag2.name)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], slugify(name))
