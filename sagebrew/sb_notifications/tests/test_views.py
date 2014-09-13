import time
from datetime import datetime
from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from sb_posts.utils import save_post
from sb_notifications.views import get_notifications

class TestNotificationViews(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')

    def tearDown(self):
        call_command('clear_neo_db')

    def test_get_notification_view_success(self):
        my_dict = {'range_end': 5, 'range_start': 0,
                   'email': self.user.email}
        request = self.factory.post('/notifications/query_notifications/',
                                    data=my_dict, format='json')
        request.user = self.user
        response = get_notifications(request)

        self.assertEqual(response.status_code, 200)

    def test_get_notification_view_missing_data(self):
        my_dict = {'range_end': 5, 'range_start': 0}
        request = self.factory.post('/notifications/query_notifications/',
                                    data=my_dict, format='json')
        request.user = self.user
        response = get_notifications(request)

        self.assertEqual(response.status_code, 400)

    def test_get_notification_view_int_data(self):
        my_dict = 1337
        request = self.factory.post('/notifications/query_notifications/',
                                    data=my_dict, format='json')
        request.user = self.user
        response = get_notifications(request)

        self.assertEqual(response.status_code, 400)

    def test_get_notification_view_string_data(self):
        my_dict = 'asdfasdf'
        request = self.factory.post('/notifications/query_notifications/',
                                    data=my_dict, format='json')
        request.user = self.user
        response = get_notifications(request)

        self.assertEqual(response.status_code, 400)

    def test_get_notification_view_array_data(self):
        my_dict = []
        request = self.factory.post('/notifications/query_notifications/',
                                    data=my_dict, format='json')
        request.user = self.user
        response = get_notifications(request)

        self.assertEqual(response.status_code, 400)

    def test_get_notification_view_float_data(self):
        my_dict = 1.5
        request = self.factory.post('/notifications/query_notifications/',
                                    data=my_dict, format='json')
        request.user = self.user
        response = get_notifications(request)

        self.assertEqual(response.status_code, 400)

    def test_get_notification_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/notifications/query_notifications/',
                                    data=image, format='json')
        request.user = self.user
        response = get_notifications(request)

        self.assertEqual(response.status_code, 400)