"""

"""
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from flying_frogs.notifications.models import Notification
from flying_frogs.friends.models import FriendList
from guardian.shortcuts import ObjectPermissionChecker
from flying_frogs.address.models import Address

from flying_frogs.user_profiles.utils import (ProfileUtils, DebugProfileUtils)


class ProfileTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        self.debug_utils = DebugProfileUtils()
        self.debug_utils.set_user_profiles()
        self.password = 'test'
        self.username = 'this_test_user'
        self.speciality = 'hair'
        self.store_number = 1
        self.user_type = "PR"
        self.full_name = 'test user'
        self.work_phone = '248-345-0781'
        self.query_set_items = {
                                    'friend_requests': User,
                                    'friends': User,
                                    'notifications': Notification,
                                    'sent_friend_requests': User,
                                }
        self.owner_context_items = {
                            'company_friends': [],
                            'customer_friends': [],
                            'employee_friends': [],
                            'friend': False,
                            'full_name': self.full_name,
                            'owner': True,
                            'user_type': self.user_type,
                            'username': self.username,
                            'work_phone': self.work_phone,
                        }
        self.user = User.objects.get(username=self.username)
        self.utils = ProfileUtils(self.user, self.user)
        self.user_profile = self.utils.current_user_profile
        self.checker = ObjectPermissionChecker(self.user)

    def test_assign_standard_perm(self):
        self.assertTrue(self.checker.has_perm('user_profiles.view_own_profile',
                                                self.user_profile))



class ModelTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        self.password = 'test'
        self.username_one = 'bleib1dj'
        self.store_number = 1
        self.work_phone = '248-345-0781'
        self.street = '3187 Bennington Dr.'
        self.user_one = User.objects.get(username=self.username_one)
        self.address = Address.objects.get(street=self.street)
        self.description = 'Description'

    def assertProfile(self, profile, user_type, username):
        self.assertEqual(profile.user.username, username)
        self.assertEqual(profile.lower_username, username.lower())
        self.assertEqual(profile.user_type, user_type)
        self.assertEqual(profile.address, self.address)
        self.assertEqual(profile.primary_phone, self.work_phone)
        self.assertEqual(profile.description, self.description)

