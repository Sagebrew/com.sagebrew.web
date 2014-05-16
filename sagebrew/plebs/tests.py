from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from guardian.shortcuts import ObjectPermissionChecker
from user_profiles.views import get_user_profile
from user_profiles.models import (USER_TYPES)
from flying_frogs.friends.views import friend_button_press

EMPLOYEE_TYPE = USER_TYPES[0][0]
COMPANY_TYPE = USER_TYPES[1][0]
CUSTOMER_TYPE = USER_TYPES[2][0]


class FriendListTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        self.client.get('/user_profiles/load_db/')
        self.password = 'test'
        self.username = 'bleib1dj'
        self.employee_one = User.objects.get(username=self.username)
        self.empl_one_prof = self.employee_one.get_profile()
        self.employee_two = User.objects.get(username='welto1ge')
        self.empl_two_prof = self.employee_two.get_profile()
        self.customer_one = User.objects.get(username='aeown@152')
        self.cust_one_prof = self.customer_one.get_profile()
        self.customer_two = User.objects.get(username='mwisner')
        self.cust_two_prof = self.customer_two.get_profile()
        self.company_one = User.objects.get(username='Inseptus')
        self.com_one_prof = self.company_one.get_profile()
        self.company_two = User.objects.get(username='ziggzi')
        self.com_two_prof = self.company_two.get_profile()
        self.checker_empl_one = ObjectPermissionChecker(self.employee_one)
        self.checker_empl_two = ObjectPermissionChecker(self.employee_two)
        self.employee_one_profile = get_user_profile(
                                        self.employee_one.username,
                                        self.empl_one_prof.user_type)
        self.employee_two_profile = get_user_profile(
                                        self.employee_two.username,
                                        self.empl_two_prof.user_type)

    def test_send_friend_request(self):
        '''
        Currently this test assumes that there are three profiles associated
        with the user profile and therefore depends on another module to be
        used. This app actually works with a single profile being defined
        and the default User model being used from django but since it was
        created with the user_profile's app in mind for robustness of both
        apps I attempted to cover all possibilities although I don't believe
        this is necessary since sending the request is based on a User
        and not a profile.
        '''
        "Assert employees can be sent friend requests"
        self.empl_one_prof.friends.send_friend_request(self.employee_two)
        self.assertEqual(
            self.empl_two_prof.friends.pending_received_list.get(
                                username__exact=self.employee_one.username),
            self.employee_one)

        "Assert customers can be sent friend requests"
        self.empl_one_prof.friends.send_friend_request(self.customer_one)
        self.assertEqual(
            self.cust_one_prof.friends.pending_received_list.get(
                                username__exact=self.employee_one.username),
            self.employee_one)

        "Assert companies can be sent friend requests"
        self.empl_one_prof.friends.send_friend_request(self.company_one)
        self.assertIn(self.employee_one,
            self.com_one_prof.friends.pending_received_list.all())

        "Assert all friends were added to employee one's pending sent list"
        self.assertIn(self.employee_two,
            self.empl_one_prof.friends.pending_sent_list.all())
        self.assertIn(self.customer_one,
            self.empl_one_prof.friends.pending_sent_list.all())
        self.assertIn(self.company_one,
            self.empl_one_prof.friends.pending_sent_list.all())

    def test_accept_friend_request(self):
        self.empl_one_prof.friends.send_friend_request(self.employee_two)
        self.empl_two_prof.friends.accept_friend_request(self.employee_one)
        self.assertTrue(self.checker_empl_one.has_perm(
                                        'user_profiles.view_friend_profile',
                                        self.employee_two_profile))
        self.assertTrue(self.checker_empl_two.has_perm(
                                        'user_profiles.view_friend_profile',
                                        self.employee_one_profile))
        self.assertIn(self.employee_two,
                        self.empl_one_prof.friends.user_list.all())
        self.assertIn(self.employee_one,
                        self.empl_two_prof.friends.user_list.all())
        self.assertNotIn(self.employee_two,
                        self.empl_one_prof.friends.pending_sent_list.all())
        self.assertNotIn(self.employee_one,
                        self.empl_two_prof.friends.pending_received_list.all())

    def test_decline_friend_request(self):
        self.empl_one_prof.friends.send_friend_request(self.employee_two)
        self.empl_two_prof.friends.decline_friend_request(self.employee_one)
        self.assertFalse(self.checker_empl_one.has_perm(
                                        'user_profiles.view_friend_profile',
                                        self.employee_two_profile))
        self.assertFalse(self.checker_empl_two.has_perm(
                                        'user_profiles.view_friend_profile',
                                        self.employee_one_profile))
        self.assertNotIn(self.employee_two,
                        self.empl_one_prof.friends.pending_sent_list.all())
        self.assertNotIn(self.employee_one,
                        self.empl_two_prof.friends.pending_received_list.all())

    def test_remove_friend(self):
        self.empl_one_prof.friends.send_friend_request(self.employee_two)
        self.empl_two_prof.friends.accept_friend_request(self.employee_one)
        self.empl_two_prof.friends.remove_friend(self.employee_one)
        self.assertNotIn(self.employee_one,
                        self.empl_two_prof.friends.user_list.all())
        self.assertNotIn(self.employee_two,
                        self.empl_one_prof.friends.user_list.all())

    def test_is_friend(self):
        self.empl_one_prof.friends.send_friend_request(self.employee_two)
        self.empl_two_prof.friends.accept_friend_request(self.employee_one)
        self.assertTrue(self.empl_one_prof.friends.is_friend(
                        self.employee_two))

    def test_check_sent_pending(self):
        self.empl_one_prof.friends.send_friend_request(self.employee_two)
        self.assertTrue(self.empl_one_prof.friends.check_sent_pending(
                        self.employee_two))

    def test_check_received_pending(self):
        self.empl_one_prof.friends.send_friend_request(self.employee_two)
        self.assertTrue(self.empl_two_prof.friends.check_received_pending(
                        self.employee_one))

    def test_get_friends_subset(self):
        self.empl_one_prof.friends.send_friend_request(self.employee_two)
        self.empl_one_prof.friends.send_friend_request(self.customer_one)
        self.empl_one_prof.friends.send_friend_request(self.company_one)
        self.empl_two_prof.friends.accept_friend_request(self.employee_one)
        self.cust_one_prof.friends.accept_friend_request(self.employee_one)
        self.com_one_prof.friends.accept_friend_request(self.employee_one)
        self.assertIn(self.employee_two,
            self.empl_one_prof.friends.get_friends_subset(EMPLOYEE_TYPE))
        self.assertIn(self.customer_one,
            self.empl_one_prof.friends.get_friends_subset(CUSTOMER_TYPE))
        self.assertIn(self.company_one,
            self.empl_one_prof.friends.get_friends_subset(COMPANY_TYPE))

    def test_friend_button_press(self):
        '''
        Based on what is happening when this test executes I'm wondering if
        the return True statement on line 32 of friends views.py is actually
        necessary...
        '''
        self.client.login(username=self.username,
                                        password=self.password)
        response = self.client.post(
                        '/user_profiles/welto1ge/',
                        {'friend_request': 'Submit', })
        self.assertFalse(friend_button_press(response,
                            self.employee_one,
                            self.employee_two))
        self.assertIn(self.employee_two,
                    self.empl_one_prof.friends.pending_sent_list.all())
        self.assertIn(self.employee_one,
                    self.empl_two_prof.friends.pending_received_list.all())

        response = self.client.post(
                        '/user_profiles/welto1ge/',
                        {self.employee_two.username: 'Accept', })
        self.assertFalse(friend_button_press(response,
                            self.employee_one,
                            self.employee_two))
        self.assertIn(self.employee_two,
                    self.empl_one_prof.friends.user_list.all())
        self.assertIn(self.employee_one,
                    self.empl_two_prof.friends.user_list.all())
        response = self.client.post(
                        '/user_profiles/welto1ge/',
                        {self.employee_two.username: 'Remove', })
        self.assertFalse(friend_button_press(response,
                            self.employee_one,
                            self.employee_two))
        self.assertNotIn(self.employee_two,
                    self.empl_one_prof.friends.user_list.all())
        self.assertNotIn(self.employee_one,
                    self.empl_two_prof.friends.user_list.all())
        response = self.client.post(
                        '/user_profiles/welto1ge/',
                        {self.employee_two.username: 'Decline', })
        self.assertFalse(friend_button_press(response,
                            self.employee_one,
                            self.employee_two))
        self.assertNotIn(self.employee_two,
                    self.empl_one_prof.friends.user_list.all())
        self.assertNotIn(self.employee_one,
                    self.empl_two_prof.friends.user_list.all())
