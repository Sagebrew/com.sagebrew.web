from uuid import uuid1

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from logging import getLogger
logger = getLogger('loggly_logs')


class UploadEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('upload-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-list')
        data = {'false-img-key': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-list')
        response = self.client.post(url, 1111111, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-list')
        response = self.client.post(url, "string", format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-list')
        response = self.client.post(url, 111.1111, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        uuid = str(uuid1())
        with open("sb_posts/tests/images/test_image.jpg", 'rb') as image:
            data = {"file": image}
            url = reverse('upload-list') + "?object_uuid=" + uuid
            response = self.client.post(url, data, format='multipart')
            self.assertEqual({'file_size': 2560, 'type': 'uploadedobject',
                              'id': uuid,
                              'file_format': u'jpeg'},
                             response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        uuid = str(uuid1())
        with open("sb_posts/tests/images/test_image.jpg", 'rb') as image:
            data = {"file": image}
            url = reverse('upload-list') + "?object_uuid=" + uuid
            response = self.client.post(url, data, format='multipart')
            self.assertEqual({'file_size': 2560, 'type': 'uploadedobject',
                              'id': uuid,
                              'file_format': u'jpeg'},
                             response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("upload-detail", kwargs={"object_uuid": uuid})
        response = self.client.delete(url)
        self.assertEqual({"detail": None}, response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_no_object_delete(self):
        self.client.force_authenticate(user=self.user)
        uuid = str(uuid1())
        url = reverse("upload-detail", kwargs={"object_uuid": uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_crop(self):
        self.client.force_authenticate(user=self.user)
        uuid = str(uuid1())
        with open("sb_posts/tests/images/test_image.jpg", 'rb') as image:
            data = {"file": image}
            url = reverse('upload-list') + "?croppic=true&object_uuid=" + uuid
            response = self.client.post(url, data, format='multipart')
            self.assertEqual({"status": "success",
                              "url": response.data['url'],
                              "width": 80,
                              "height": 80},
                             response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            uploaded_url = response.data['url']
            logger.info(uploaded_url)
        crop_url = reverse('upload-crop', kwargs={'object_uuid': uuid}) + \
            "?resize=true&croppic=true"
        crop_data = {
            "crop_width": 40,
            "crop_height": 40,
            "image_x1": 4,
            "image_y1": 4,
            "resize_width": 100,
            "resize_height": 100,
            "imgUrl": str(uploaded_url)
        }
        response = self.client.post(crop_url, crop_data, format='multipart')
        self.assertEqual({"status": "success",
                          "url": response.data['url'],
                          "profile": response.data['profile']},
                         response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
