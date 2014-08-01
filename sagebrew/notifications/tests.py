"""
TestCases for the Notification models. Currently the notification model
is not very expansive so there are not many tests but there is test
coverage for each of the model's modules.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from flying_frogs.notifications.models import (NOTIFICATIONS,
                                               Notification,
                                               NOTIFICATION_MESSAGE)


class NotificationTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        self.client.get('/user_profiles/load_db/')
        self.password = 'test'
        self.username = 'bleib1dj'
        self.username_two = 'welto1ge'
        self.notification_type = 'accept_friend_request'
        self.user = User.objects.get(username=self.username)
        self.user_two = User.objects.get(username=self.username_two)
        self.notification_message_hard_check = ("Devon Bleibtrey has sent" +
                                                " you a friend request")

    def test_notification_message(self):
        '''
        Test: Notification Message
        Coverage: Tests that the macro NOTIFICATION_MESSAGE correctly takes
                  a string and a notification message based on a provided
                  key which is based on the type of notification that is
                  being added to the owner's list of notifications.
                  Also has a hard check to ensure that the message is being
                  formed based on the correct item in the array of returned
                  values in the NOTIFICATIONS dict.

                  Covers all of the notifications available in the
                  NOTIFICATIONS dict but only hard checks one of them.
        '''
        for key in NOTIFICATIONS:
            self.assertEqual(NOTIFICATION_MESSAGE('Devon Bleibtrey',
                                                  NOTIFICATIONS[key][1]),
                             'Devon Bleibtrey ' + NOTIFICATIONS[key][1])
            if (key == 'send_friend_request'):
                self.assertEqual(NOTIFICATION_MESSAGE('Devon Bleibtrey',
                                                      NOTIFICATIONS[key][1]),
                                 self.notification_message_hard_check)

    def test_notification_viewed(self):
        '''
        Test: Notification Viewed
        Coverage: Ensures that once a notification is created and then a view
                  indicates that the user has viewed the notification that the
                  viewed attribute of the notification is changed from False
                  to True.
        '''
        profile = self.user_two.get_profile()
        notification = Notification(owner=self.user,
                                    message=NOTIFICATIONS[
                                        self.notification_type],
                                    notification_type=self.notification_type)
        notification.save()
        profile.notifications.add(notification)
        profile.save()
        viewed_notification = profile.notifications.get(id=notification.id)
        viewed_notification.notification_viewed()
        viewed_notification.save()
        self.assertEqual(viewed_notification.viewed, True)
