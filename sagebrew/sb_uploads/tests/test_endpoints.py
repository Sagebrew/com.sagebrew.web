import time
from uuid import uuid1

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from neomodel import UniqueProperty

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_uploads.neo_models import URLContent


class UploadEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.client.force_authenticate(user=self.user)
        self.uuid = str(uuid1())
        with open("sb_posts/tests/images/test_image.jpg", 'rb') as image:
            data = {"file": image}
            url = reverse('upload-list') + "?object_uuid=" + self.uuid
            response = self.client.post(url, data, format='multipart')
            self.url = response.data['url']
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

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
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        uuid = str(uuid1())
        with open("sb_posts/tests/images/test_image.jpg", 'rb') as image:
            data = {"file": image}
            url = reverse('upload-list') + "?object_uuid=" + uuid
            response = self.client.post(url, data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("upload-detail", kwargs={"object_uuid": uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_no_object_delete(self):
        self.client.force_authenticate(user=self.user)
        uuid = str(uuid1())
        url = reverse("upload-detail", kwargs={"object_uuid": uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

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

    def test_get_height(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-detail', kwargs={"object_uuid": self.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(80, response.data['height'])

    def test_get_width(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-detail', kwargs={"object_uuid": self.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(80, response.data['width'])

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-detail', kwargs={"object_uuid": self.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.url, response.data['url'])

    def test_get_file_size(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-detail', kwargs={"object_uuid": self.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(2560, response.data['file_size'])

    def test_get_file_format(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-detail', kwargs={"object_uuid": self.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('jpeg', response.data['file_format'])

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-detail', kwargs={"object_uuid": self.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.uuid, response.data['id'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('upload-detail', kwargs={"object_uuid": self.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('uploadedobject', response.data['type'])


class URLContentEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.client.force_authenticate(user=self.user)
        self.client.logout()
        self.test_url = "example.com"
        try:
            self.url_content = URLContent(url=self.test_url,
                                          description="this is a test "
                                                      "description",
                                          title="this is a test title",
                                          selected_image="http://i.imgur.com"
                                                         "/7ItPc2M.jpg")\
                .save()
        except UniqueProperty:
            self.url_content = URLContent.nodes.get(url=self.test_url)

    def test_unauthorized(self):
        url = reverse('urlcontent-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-detail',
                      kwargs={'object_uuid': self.url_content.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_description(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-detail',
                      kwargs={'object_uuid': self.url_content.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['description'],
                         self.url_content.description)

    def test_get_title(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-detail',
                      kwargs={'object_uuid': self.url_content.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['title'],
                         self.url_content.title)

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-detail',
                      kwargs={'object_uuid': self.url_content.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['url'],
                         self.url_content.url)

    def test_get_selected_image(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-detail',
                      kwargs={'object_uuid': self.url_content.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['selected_image'],
                         self.url_content.selected_image)

    def test_create_with_og(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        data = {
            "url": "https://twitter.com/twitter/status/628335876867645440"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['title'], 'Twitter on Twitter')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_just_image(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        data = {
            "url": "http://i.imgur.com/Mh17Blf.jpg"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['selected_image'], data['url'])

    def test_create_not_og(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        data = {
            "url": "http://www.crummy.com/software/"
                   "BeautifulSoup/bs4/doc/#the-name-argument"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'],
                         "Beautiful Soup Documentation  "
                         "Beautiful Soup 4.4.0 documentation")

    def test_create_explicit(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        data = {
            "url": "pornhub.com"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_explicit'])

    def test_create_html(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list') + "?html=true"
        data = {
            "url": "example.com"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['html'], '')

    def test_create_invalid_status_code(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        data = {
            "url": "https://github.com/asdfasdfasdfashdfjhalsdhf"
                   "kjabsldjghalsjdbhlkj1;3ouihr13/"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_friend(self):
        self.client.force_authenticate(user=self.user)
        email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(email2)
        while not res['task_id'].ready():
            time.sleep(.1)
        friend = Pleb.nodes.get(email=email2)
        content = URLContent(url="test.com").save()
        content.owned_by.connect(friend)
        self.pleb.friends.connect(friend)
        friend.friends.connect(self.pleb)
        url = reverse('urlcontent-list') + "?user=%s" % friend.username
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)

    def test_list_not_friend(self):
        self.client.force_authenticate(user=self.user)
        email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(email2)
        while not res['task_id'].ready():
            time.sleep(.1)
        friend = Pleb.nodes.get(email=email2)
        content = URLContent(url="https://www.test.com/our-platform.html")\
            .save()
        content.owned_by.connect(friend)
        self.pleb.friends.disconnect(friend)
        friend.friends.disconnect(self.pleb)
        url = reverse('urlcontent-list') + "?user=%s" % friend.username
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_create_url_timeout(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        data = {
            "url": "http://10.255.255.1"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_image_with_double_slash(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        data = {
            "url": "https://www.reddit.com/"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_connection_error(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('urlcontent-list')
        data = {
            "url": "https://sagebrew.com/"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
