import time
from datetime import datetime
from dateutil import parser

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_posts.neo_models import Post
from sb_registration.utils import create_user_util_test
from sb_notifications.neo_models import Notification


class UserNotificationRetrieveTest(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'notification'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_unauthorized(self):
        url = reverse('notification-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        self.client.force_authenticate(user=self.user)
        for notification in self.pleb.notifications.all():
            notification.delete()
        url = reverse('notification-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 0)

    def test_list_with_items(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-list')
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)

    def test_list_seen_api(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = "%s?seen=true" % reverse('notification-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'], [])

    def test_list_seen_render(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = "%s?seen=true" % reverse('notification-render')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results']['unseen'], 0)

    def test_list_render_unseen(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-render')
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['results']['unseen'], 0)

    def test_list_render_ids(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-render')
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data['results']['ids']), 0)

    def test_list_render_html(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-render')
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data['results']['html']), 0)

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['id'], notification.object_uuid)

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['type'], 'notification')

    def test_get_seen(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertFalse(response.data['seen'])

    def test_get_time_sent(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(parser.parse(response.data['time_sent']).isoformat(),
                         notification.time_sent.isoformat())

    def test_get_time_seen(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = "%s?seen=true" % reverse('notification-list')
        self.client.get(url, format='json')
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        notification.refresh()
        self.assertEqual(parser.parse(response.data['time_seen']).isoformat(),
                         notification.time_seen.isoformat())

    def test_get_about(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['about'], None)

    def test_get_sent(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertFalse(response.data['sent'])

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['url'], None)

    def test_get_action_name(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['action_name'],
                         "This is it! a notification")

    def test_get_notification_from(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertIsInstance(response.data['notification_from'], dict)

    def test_get_notification_id(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification(
            action_name="This is it! a notification").save()
        notification.notification_from.connect(self.pleb)
        notification.notification_to.connect(self.pleb)
        self.pleb.notifications.connect(notification)
        url = reverse('notification-detail',
                      kwargs={'object_uuid': notification.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['notification_from']['id'],
                         self.pleb.username)
