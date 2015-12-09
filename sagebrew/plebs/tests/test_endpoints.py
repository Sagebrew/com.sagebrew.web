import time
from uuid import uuid1
import shortuuid
from collections import OrderedDict

from django.utils.text import slugify
from django.templatetags.static import static
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings

from neomodel import db, DoesNotExist

from rest_framework import status
from rest_framework.test import APITestCase

from api.utils import wait_util
from sagebrew import errors
from sb_public_official.neo_models import PublicOfficial
from plebs.neo_models import (Pleb, FriendRequest, Address, BetaUser,
                              PoliticalParty, ActivityInterest)
from sb_privileges.neo_models import Privilege, SBAction
from sb_quests.neo_models import Position, Quest
from sb_updates.neo_models import Update
from sb_locations.neo_models import Location
from sb_missions.neo_models import Mission
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test
from sb_posts.neo_models import Post
from sb_solutions.neo_models import Solution
from sb_donations.neo_models import Donation


class MeEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('me-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_get_username(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual('test_test', response.data['username'])

    def test_get_first_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['first_name'])

    def test_get_last_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['last_name'])

    def test_get_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['profile_pic'],
                         static("images/sage_coffee_grey-01.png"))

    def test_get_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['wallpaper_pic'],
                         static("images/wallpaper_western.jpg"))

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual('http://testserver/user/test_test/',
                         response.data['url'])

    def test_get_privileges(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['privileges'])

    def test_get_actions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        cache.clear()
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['actions'])

    def test_get_actions_populated(self):
        self.client.force_authenticate(user=self.user)
        action = SBAction(resource="test_action").save()
        self.pleb.actions.connect(action)
        cache.clear()
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.pleb.actions.disconnect(action)
        self.assertEqual(['test_action'], response.data['actions'])

    def test_get_privileges_populated(self):
        self.client.force_authenticate(user=self.user)
        privilege = Privilege(name="test_privilege").save()
        self.pleb.privileges.connect(privilege)
        cache.clear()
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.pleb.privileges.disconnect(privilege)
        privilege.delete()
        self.assertEqual(['test_privilege'], response.data['privileges'])

    def test_get_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/v1/profiles/test_test/",
                         response.data['href'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual("profile", response.data['type'])

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual("test_test", response.data['id'])

    def test_get_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['reputation'])

    def test_get_populated_wallpaper(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        wallpaper = self.pleb.wallpaper_pic
        self.pleb.wallpaper_pic = "http://helloworld.com/this.jpeg"
        self.pleb.save()
        cache.set(self.pleb.username, self.pleb)
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['wallpaper_pic'],
                         self.pleb.wallpaper_pic)
        self.pleb.wallpaper_pic = wallpaper
        self.pleb.save()

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        data = {
            "wallpaper_pic": "http://example.com/",
            "profile_pic": "http://example.com/"
        }
        res = self.client.put(url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_donations(self):
        quest = Quest(owner_username=str(uuid1())).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        donation = Donation().save()
        self.pleb.donations.connect(donation)
        donation.owned_by.connect(self.pleb)
        donation.mission.connect(mission)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-donations')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_donations_html(self):
        quest = Quest(owner_username=str(uuid1())).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        donation = Donation().save()
        self.pleb.donations.connect(donation)
        donation.owned_by.connect(self.pleb)
        donation.mission.connect(mission)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-donations') + "?html=true"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_sagebrew_donations(self):
        donation = Donation().save()
        self.pleb.donations.connect(donation)
        donation.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['sagebrew_donations'], [donation.object_uuid])

    def test_donations_with_only_sagebrew_donation(self):
        for donation in Donation.nodes.all():
            donation.delete()
        donation = Donation().save()
        self.pleb.donations.connect(donation)
        donation.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-donations')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['results'])
        donation.delete()

    def test_add_party(self):
        name = 'democratic_party'
        party = PoliticalParty(name=name).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-parties')
        data = {"names": [name]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(name, response.data['names'])
        self.assertIn(name, self.pleb.get_political_parties())
        for political_party in self.pleb.party_affiliations.all():
            self.pleb.party_affiliations.disconnect(political_party)
        party.delete()

    def test_add_no_parties(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-parties')
        data = {"names": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(self.pleb.get_political_parties()), 0)

    def test_add_multiple_parties(self):
        name = 'democratic_party'
        name2 = 'republican_party'
        party = PoliticalParty(name=name).save()
        party2 = PoliticalParty(name=name2).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-parties')
        data = {"names": [name, name2]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(name, response.data["names"])
        self.assertIn(name2, response.data["names"])
        self.assertIn(name, self.pleb.get_political_parties())
        self.assertIn(name2, self.pleb.get_political_parties())
        for political_party in self.pleb.party_affiliations.all():
            self.pleb.party_affiliations.disconnect(political_party)
        party.delete()
        party2.delete()

    def test_non_existent_parties(self):
        for political_party in self.pleb.party_affiliations.all():
            self.pleb.party_affiliations.disconnect(political_party)
        name = 'other_party'
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-parties')
        data = {"names": [name]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["names"], [])
        self.assertEqual(len(self.pleb.get_political_parties()), 0)

    def test_non_string_party(self):
        name = 5
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-parties')
        data = {"names": [name]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['names'], [])

    def test_non_array_party(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-parties')
        data = {"names": "hello"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['names'],
                         [u'Expected a list of items but got type "unicode".'])

    def test_exists_and_does_not_exist_parties(self):
        name = 'democratic_party'
        name2 = 'republican_party'
        party = PoliticalParty(name=name).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-parties')
        data = {"names": [name, name2]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(name, response.data["names"])
        self.assertNotIn(name2, response.data["names"])
        self.assertIn(name, self.pleb.get_political_parties())
        self.assertNotIn(name2, self.pleb.get_political_parties())
        for political_party in self.pleb.party_affiliations.all():
            self.pleb.party_affiliations.disconnect(political_party)
        party.delete()

    def test_add_interest(self):
        name = 'volunteering'
        activity = ActivityInterest(name=name).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-interests')
        data = {"interests": [name]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(name, response.data['interests'])
        self.assertIn(name, self.pleb.get_activity_interests())
        for interest in self.pleb.activity_interests.all():
            self.pleb.activity_interests.disconnect(interest)
        activity.delete()

    def test_add_no_interests(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-interests')
        data = {"interests": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(self.pleb.get_activity_interests()), 0)

    def test_add_multiple_interests(self):
        name = 'volunteering'
        name2 = 'attending_events'
        activity = ActivityInterest(name=name).save()
        activity2 = ActivityInterest(name=name2).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-interests')
        data = {"interests": [name, name2]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(name, response.data["interests"])
        self.assertIn(name2, response.data["interests"])
        self.assertIn(name, self.pleb.get_activity_interests())
        self.assertIn(name2, self.pleb.get_activity_interests())
        for interest in self.pleb.activity_interests.all():
            self.pleb.activity_interests.disconnect(interest)
        activity.delete()
        activity2.delete()

    def test_non_existent_interests(self):
        for activity in self.pleb.activity_interests.all():
            self.pleb.activity_interests.disconnect(activity)
        name = 'other_interest'
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-interests')
        data = {"interests": [name]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["interests"], [])
        self.assertEqual(len(self.pleb.get_activity_interests()), 0)

    def test_non_string_interest(self):
        name = 5
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-interests')
        data = {"interests": [name]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['interests'], [])

    def test_non_array_interest(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-interests')
        data = {"interests": "hello"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['interests'],
                         [u'Expected a list of items but got type "unicode".'])

    def test_exists_and_does_not_exist_interests(self):
        name = 'volunteering'
        name2 = 'attending_events'
        activity = ActivityInterest(name=name).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('me-add-interests')
        data = {"interests": [name, name2]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(name, response.data["interests"])
        self.assertNotIn(name2, response.data["interests"])
        self.assertIn(name, self.pleb.get_activity_interests())
        self.assertNotIn(name2, self.pleb.get_activity_interests())
        for interest in self.pleb.activity_interests.all():
            self.pleb.activity_interests.disconnect(interest)
        activity.delete()


class SentFriendRequestEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'friend_requests'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email2)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.url = "http://testserver"
        self.friend_request = FriendRequest().save()
        self.pleb.friend_requests_received.connect(self.friend_request)
        self.pleb.friend_requests_sent.connect(self.friend_request)
        self.friend_request.request_to.connect(self.pleb)
        self.friend_request.request_from.connect(self.pleb2)

    def test_list_unauthorized(self):
        url = reverse('sent_friend_request-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_unauthorized(self):
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_friend_request_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.friend_request.object_uuid)

    def test_get_friend_request_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], "friend_request")

    def test_get_friend_request_seen(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['seen'])

    def test_get_friend_request_time_sent(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_sent'],
                         self.friend_request.time_sent.isoformat()[:-6] + 'Z')

    def test_get_friend_request_time_seen(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_seen'],
                         self.friend_request.time_seen)

    def test_get_friend_request_response(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['response'])

    def test_get_friend_request_from_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['from_user'], dict)

    def test_get_friend_request_to_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['to_user'], dict)

    def test_get_friend_request_to_user_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_incorrect_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.put(url, data={'fake_key': 'fake value'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_friend_request_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-list')
        response = self.client.get(url)
        self.assertGreater(response.data['count'], 0)

    def test_get_friend_request_list_no_cache(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        url = reverse('sent_friend_request-list')
        response = self.client.get(url)
        self.assertGreater(response.data['count'], 0)

    def test_get_friend_request_list_cache(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-list')
        self.client.get(url)
        response = self.client.get(url)
        self.assertGreater(response.data['count'], 0)


class FriendManagerEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'friend'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email2)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.pleb.friends.connect(self.pleb2)
        self.pleb2.friends.connect(self.pleb)
        self.url = "http://testserver"

    def test_list_unauthorized(self):
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_detail_unauthorized(self):
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_friend_request_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.pleb2.username)

    def test_get_friend_request_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], "profile")

    def test_get_friend_request_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['profile_pic'],
                         static('images/sage_coffee_grey-01.png'))

    def test_get_friend_request_first_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['first_name'], 'test')

    def test_get_friend_request_last_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['last_name'], 'test')

    def test_get_friend_request_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['wallpaper_pic'],
                         static('images/wallpaper_western.jpg'))

    def test_get_friend_request_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['url'], 'http://testserver/user'
                                               '/test_test1/')

    def test_get_friend_request_privileges(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['privileges'], [])

    def test_get_friend_request_actions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['actions'], [])

    def test_get_friend_request_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['href'], 'http://testserver/'
                                                'v1/profiles/test_test1/')

    def test_get_friend_request_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['reputation'], 0)

    def test_get_friend_request_to_user_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.pleb.friends.connect(self.pleb2)
        self.pleb2.friends.connect(self.pleb)


class ProfileEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_unauthorized(self):
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        data = {'detail': 'TBD'}
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

    def test_get_username(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual('test_test', response.data['username'])

    def test_get_first_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['first_name'])

    def test_get_is_verified(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertTrue(response.data['is_verified'])

    def test_get_last_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['last_name'])

    def test_get_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['profile_pic'],
                         static('images/sage_coffee_grey-01.png'))

    def test_get_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['profile_pic'],
                         static('images/sage_coffee_grey-01.png'))

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual('http://testserver/user/test_test/',
                         response.data['url'])

    def test_get_privileges(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['privileges'])

    def test_get_actions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['actions'])

    def test_get_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/v1/profiles/test_test/",
                         response.data['href'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("profile", response.data['type'])

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("test_test", response.data['id'])

    def test_get_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['reputation'])

    def test_get_pleb_no_cache(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        cache.clear()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pleb_quest_expand(self):
        for quest in self.pleb.quest.all():
            quest.delete()
        cache.clear()
        quest = Quest(object_uuid=self.pleb.username).save()
        self.pleb.quest.connect(quest)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username}) + "?expand=true"
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['quest']['owner_username'],
                         self.user.username)

    def test_create_pleb(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data, {'detail': 'TBD'})
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)


class ProfileContentMethodTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_pleb_questions(self):
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pleb_question_id(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['id'],
                         question.object_uuid)

    def test_get_pleb_question_type(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['type'],
                         'question')

    def test_get_pleb_question_object_uuid(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['object_uuid'],
                         question.object_uuid)

    def test_get_pleb_question_content(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'],
                         question.content)

    def test_get_pleb_question_profile(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         "test_test")

    def test_get_pleb_question_url(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['url'],
                         "http://testserver/conversations/"
                         "%s/%s/" % (question.object_uuid,
                                     slugify(question.title)))

    def test_get_pleb_question_title(self):
        for item in Question.nodes.all():
            item.delete()
        title = str(uuid1())
        question = Question(
            title=title,
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['title'], title)

    def test_get_pleb_question_invalid_query(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?filter=error" % reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data, errors.QUERY_DETERMINATION_EXCEPTION)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_pleb_question_public_content(self):
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-public-content', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertGreater(response.data['count'], 0)

    def test_get_pleb_public_content_invalid_query(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?filter=error" % reverse('profile-public-content', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data, errors.QUERY_DETERMINATION_EXCEPTION)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_pleb_public_content_id(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-public-content', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['id'],
                         question.object_uuid)


class ProfileFriendsMethodTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_pleb_friends_type(self):
        friend = Pleb(username=shortuuid.uuid()).save()
        self.pleb.friends.connect(friend)
        friend.friends.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-friends', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['type'], 'profile')

    def test_get_pleb_friends_html(self):
        friend = Pleb(username=shortuuid.uuid()).save()
        self.pleb.friends.connect(friend)
        friend.friends.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-friends', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BaseUserTests(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email)
        create_user_util_test(self.email2)
        self.user = User.objects.get(email=self.email)
        self.unit_under_test = User.objects.get(email=self.email2)
        self.unit_under_test_name = "user"

    def test_unauthorized_message(self):
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['detail'],
                         'Authentication credentials were not provided.')

    def test_unauthorized_status(self):
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'asset_uri': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_no_birthday(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['birthday'], ['This field is required.'])

    def test_update_no_email(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['email'], ['This field is required.'])

    def test_update_no_last_name(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['last_name'],
                         ['This field is required.'])

    def test_update_does_not_exist_status(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"username": str(shortuuid.uuid())})
        data = {'status_code': status.HTTP_404_NOT_FOUND,
                'detail': 'Not found.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_does_not_exist_message(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"username": str(shortuuid.uuid())})
        data = {'status_code': status.HTTP_404_NOT_FOUND,
                'detail': 'Not found.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['detail'], 'Not found.')

    def test_update_bad_request(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_list(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
                'detail': 'Method "PUT" not allowed.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        data = None
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_list_detail(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_delete_list_status(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_read_username(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['username'], 'test_test1')

    def test_read_profile(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['profile'],
                         'http://testserver/v1/profiles/test_test1/')

    def test_read_first_name(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['first_name'], 'test')

    def test_read_last_name(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['last_name'], 'test')

    def test_read_href(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['href'],
                         'http://testserver/v1/users/test_test1/')

    def test_read_type(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['type'], 'user')

    def test_read_id(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['id'], 'test_test1')

    def test_read_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, OrderedDict)

    def test_read_is_not_self(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_is_not_self_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['detail'],
                         'You do not have permission to perform this action.')

    def test_update_is_not_self_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FriendRequestListTest(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'friend_request'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_unauthorized(self):
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
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
        cache.clear()
        for friend_request in self.pleb.friend_requests_received.all():
            friend_request.delete()
        url = reverse('friend_request-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 0)

    def test_list_with_items(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = reverse('friend_request-list')
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)

    def test_list_seen_api(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = "%s?seen=true" % reverse('friend_request-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'], [])

    def test_list_seen_render(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = "%s?seen=true" % reverse('friend_request-render')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results']['unseen'], 0)

    def test_list_render_unseen(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = reverse('friend_request-render')
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['results']['unseen'], 0)

    def test_list_render_ids(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = reverse('friend_request-render')
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data['results']['ids']), 0)

    def test_list_render_html(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = reverse('friend_request-render')
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data['results']['html']), 0)


class PlebPresidentTest(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="Michigan",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)

    def test_unauthorized(self):
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("<small>Sorry we could not find"
                         " your President. Please alert us to our "
                         "error!</small>", response.data)

    def test_list_president(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        president = PublicOfficial(first_name="Debbie", last_name="Stab",
                                   state="Michigan",
                                   bioguideid=shortuuid.uuid(),
                                   full_name="Debbie Stab [Dem]")
        president.save()
        for president in self.pleb.president.all():
            self.pleb.president.disconnect(president)
        self.pleb.president.connect(president)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_president_cache(self):
        president = PublicOfficial(first_name="Debbie", last_name="Stab",
                                   state="Michigan",
                                   bioguideid=shortuuid.uuid(),
                                   full_name="Debbie Stab [Dem]")
        president.save()
        for president in self.pleb.president.all():
            self.pleb.president.disconnect(president)
        self.pleb.president.connect(president)
        self.client.force_authenticate(user=self.user)
        query = "MATCH (a:Pleb {username: '%s'})-[:HAS_PRESIDENT]->" \
                "(s:PublicOfficial) RETURN s" % self.user.username
        res, col = db.cypher_query(query)
        senators = [PublicOfficial.inflate(row[0]) for row in res]
        cache.set("%s_senators" % self.user.username, senators)
        url = reverse('profile-president',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_president_html(self):
        cache.clear()
        president = PublicOfficial(first_name="Debbie", last_name="Stab",
                                   state="Michigan",
                                   bioguideid=shortuuid.uuid(),
                                   full_name="Debbie Stab [Dem]")
        president.save()
        for president in self.pleb.president.all():
            self.pleb.president.disconnect(president)
        self.pleb.president.connect(president)
        url = "%s?html=true" % reverse('profile-president',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_potential_presidents(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        position = Position(name="President").save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)

        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-presidents',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['type'], 'quest')
        self.assertEqual(response.data[0]['owner_username'],
                         self.pleb.username)
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_presidents_cached(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        position = Position(name="President").save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-presidents',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['type'], 'quest')
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_presidents_not_active(self):
        cache.clear()
        for quest in Quest.nodes.all():
            quest.delete()
        for position in Position.nodes.all():
            position.delete()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        position = Position(name="President").save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-presidents',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_presidents_html_no_presidents(self):
        cache.clear()
        for quest in Quest.nodes.all():
            quest.delete()
        for position in Position.nodes.all():
            position.delete()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username
        ).save()
        position = Position(name="President").save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-possible-presidents',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("Currently No Registered" in response.data)
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_presidents_html(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        position = Position(name="President").save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-possible-presidents',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        position.delete()
        mission.delete()
        quest.delete()


class PlebSenatorsTest(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="Michigan",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)

    def test_unauthorized(self):
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("<small>Sorry we could not find"
                         " your Senators. Please alert us to our "
                         "error!</small>", response.data)

    def test_list_senators(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        senator1 = PublicOfficial(first_name="Debbie", last_name="Stab",
                                  state="Michigan", bioguideid=shortuuid.uuid(),
                                  full_name="Debbie Stab [Dem]")
        senator1.save()
        senator2 = PublicOfficial(first_name="Tester", last_name="Test",
                                  state="Michigan", bioguideid=shortuuid.uuid())
        senator2.save()
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        self.pleb.senators.connect(senator1)
        self.pleb.senators.connect(senator2)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_senators_cache(self):
        senator1 = PublicOfficial(first_name="Debbie", last_name="Stab",
                                  state="MI", bioguideid=shortuuid.uuid(),
                                  full_name="Debbie Stab [Dem]")
        senator1.save()
        senator2 = PublicOfficial(first_name="Tester", last_name="Test",
                                  state="MI", bioguideid=shortuuid.uuid())
        senator2.save()
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        self.pleb.senators.connect(senator1)
        self.pleb.senators.connect(senator2)
        self.client.force_authenticate(user=self.user)
        query = "MATCH (a:Pleb {username: '%s'})-[:HAS_SENATOR]->" \
                "(s:PublicOfficial) RETURN s" % self.user.username
        res, col = db.cypher_query(query)
        senators = [PublicOfficial.inflate(row[0]) for row in res]
        cache.set("%s_senators" % self.user.username, senators)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_senators_html(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        senator1 = PublicOfficial(first_name="Debbie", last_name="Stab",
                                  state="Michigan", bioguideid=shortuuid.uuid(),
                                  full_name="Debbie Stab [Dem]")
        senator1.save()
        senator2 = PublicOfficial(first_name="Tester", last_name="Test",
                                  state="MI", bioguideid=shortuuid.uuid())
        senator2.save()
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        self.pleb.senators.connect(senator1)
        self.pleb.senators.connect(senator2)
        url = "%s?html=true" % reverse('profile-senators',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_potential_senators(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="Test Location", sector="federal").save()
        location2 = Location(name="Michigan", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location2)
        location2.positions.connect(position)
        location2.encompasses.connect(location)
        location.encompassed_by.connect(location2)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['type'], 'quest')
        self.assertEqual(response.data[0]['owner_username'],
                         self.pleb.username)
        location.delete()
        location2.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_senators_cached(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="Test Location", sector="federal").save()
        location2 = Location(name="Michigan", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location2)
        location2.positions.connect(position)
        location2.encompasses.connect(location)
        location.encompassed_by.connect(location2)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-senators',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['type'], 'quest')
        location.delete()
        location2.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_senators_not_active(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        location = Location(name="Test Location", sector="federal").save()
        location2 = Location(name="Michigan", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location2)
        location2.positions.connect(position)
        location2.encompasses.connect(location)
        location.encompassed_by.connect(location2)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-senators',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        location.delete()
        location2.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_senators_html_no_senators(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        location = Location(name="Test Location", sector="federal").save()
        location2 = Location(name="Michigan", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location2)
        location2.positions.connect(position)
        location2.encompasses.connect(location)
        location.encompassed_by.connect(location2)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-possible-senators',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("Currently No Registered" in response.data)
        location.delete()
        location2.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_senators_html(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="Test Location", sector="federal").save()
        location2 = Location(name="Michigan", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location2)
        location2.positions.connect(position)
        location2.encompasses.connect(location)
        location.encompassed_by.connect(location2)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-possible-senators',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        location.delete()
        location2.delete()
        position.delete()
        mission.delete()
        quest.delete()


class PlebHouseRepresentativeTest(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="Michigan",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)

    def test_unauthorized(self):
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        for senator in self.pleb.house_rep.all():
            self.pleb.house_rep.disconnect(senator)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("<small>Sorry we could not find"
                         " your House Representative. Please alert us to our "
                         "error!</small>", response.data)

    def test_list_house_representative(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        house_representative = PublicOfficial(
            first_name="Debbie", last_name="Stab",
            state="MI", bioguideid=shortuuid.uuid(),
            full_name="Debbie Stab [Dem]",
            district=11)
        house_representative.save()
        for rep in self.pleb.house_rep.all():
            self.pleb.house_rep.disconnect(rep)
        self.pleb.house_rep.connect(house_representative)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_house_representative_cache(self):
        cache.clear()
        house_representative = PublicOfficial(
            first_name="Debbie", last_name="Stab",
            state="MI", bioguideid=shortuuid.uuid(),
            full_name="Debbie Stab [Dem]",
            district=11)
        house_representative.save()
        for house_representative in self.pleb.house_rep.all():
            self.pleb.house_rep.disconnect(house_representative)
        self.pleb.house_rep.connect(house_representative)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_house_representative_html(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        house_representative = PublicOfficial(
            first_name="Debbie", last_name="Stab",
            state="MI", bioguideid=shortuuid.uuid(),
            full_name="Debbie Stab [Dem]", district=11)
        house_representative.save()
        for house_rep in self.pleb.house_rep.all():
            self.pleb.house_rep.disconnect(house_rep)
        self.pleb.house_rep.connect(house_representative)
        url = "%s?html=true" % reverse('profile-house-representative',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_potential_house_representative(self):
        cache.clear()
        for address in self.pleb.address.all():
            address.delete()
        address = Address(street="3295 Rio Vista St",
                          city="Commerce Township", state="Michigan",
                          postal_code="48382", country="US",
                          congressional_district="11")
        address.save()
        address.owned_by.connect(self.pleb)
        self.pleb.address.connect(address)
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="11", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location)
        location.positions.connect(position)
        address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-house-representatives',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['type'], 'quest')
        self.assertEqual(response.data[0]['owner_username'],
                         self.pleb.username)
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_house_representative_cached(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="11", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location)
        location.positions.connect(position)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-house-representatives',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['type'], 'quest')
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_house_representative_not_active(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        location = Location(name="11", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location)
        location.positions.connect(position)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-house-representatives',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_house_representative_html_none(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        location = Location(name="11").save()
        position = Position(name="Test Position").save()

        position.location.connect(location)
        location.positions.connect(position)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-possible-house-representatives',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertTrue("Currently No Registered" in response.data)
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_house_representative_html(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="11", sector="federal").save()
        position = Position(name="Test Position").save()

        position.location.connect(location)
        location.positions.connect(position)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-possible-house-representatives',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertFalse("Currently No Registered" in response.data)
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()


class PlebLocalRepresentativeTest(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="Michigan",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)

    def test_list_potential_local_representative(self):
        cache.clear()
        for address in self.pleb.address.all():
            address.delete()
        address = Address(street="3295 Rio Vista St",
                          city="Commerce Township", state="Michigan",
                          postal_code="48382", country="US",
                          congressional_district="11")
        address.save()
        address.owned_by.connect(self.pleb)
        self.pleb.address.connect(address)
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="Commerce Township", sector='local').save()
        position = Position(name="Test Position", level='local').save()

        position.location.connect(location)
        location.positions.connect(position)
        address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-local-representatives',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['type'], 'quest')
        self.assertEqual(response.data[0]['owner_username'],
                         self.pleb.username)
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_local_representative_cached(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="Commerce Township", sector='local').save()
        position = Position(name="Test Position", level='local').save()

        position.location.connect(location)
        location.positions.connect(position)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-local-representatives',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['type'], 'quest')
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_local_representative_not_active(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        location = Location(name="Commerce Township", sector='local').save()
        position = Position(name="Test Position", level='local').save()

        position.location.connect(location)
        location.positions.connect(position)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-possible-local-representatives',
                      kwargs={'username': self.pleb.username})
        self.client.get(url, format='json')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_local_representative_html_none(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        location = Location(name="Commerce Township", sector='local').save()
        position = Position(name="Test Position", level='local').save()

        position.location.connect(location)
        location.positions.connect(position)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-possible-local-representatives',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertTrue("Currently No Registered" in response.data)
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()

    def test_list_potential_local_representative_html(self):
        cache.clear()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username,
            active=True).save()
        location = Location(name="Commerce Township", sector='local').save()
        position = Position(name="Test Position", level='local').save()

        position.location.connect(location)
        location.positions.connect(position)
        self.address.encompassed_by.connect(location)
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        mission.position.connect(position)
        location.addresses.connect(self.address)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-possible-local-representatives',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertFalse("Currently No Registered" in response.data)
        location.delete()
        position.delete()
        mission.delete()
        quest.delete()


class AddressEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'address'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="MI",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('address-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.address.object_uuid, response.data['id'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('address', response.data['type'])

    def test_get_street(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('3295 Rio Vista St', response.data['street'])

    def test_get_street_additional(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['street_additional'])

    def test_get_city(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['city'], "Commerce Township")

    def test_get_state(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['state'], 'MI')

    def test_get_postal_code(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['postal_code'], "48382")

    def test_get_congressional_district(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['congressional_district'], 11)

    def test_get_validated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertFalse(response.data['validated'])

    def test_address_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.get(url, format='json')

        self.assertGreater(response.data['count'], 0)

    def test_create_address(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        data = {
            'city': "Walled Lake",
            'longitude': -83.48016,
            'state': "MI",
            'street': "300 Eagle Pond Dr.",
            'postal_code': "48390-3071",
            'congressional_district': "11",
            'latitude': 42.54083
        }
        temp_loc = Location(name=data['city']).save()
        state = Location(name="Michigan").save()
        temp_loc.encompassed_by.connect(state)
        state.encompasses.connect(temp_loc)
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['congressional_district'], 11)
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address {object_uuid: "%s"}) ' \
                'RETURN b' % (self.user.username, response.data['id'])
        res, col = db.cypher_query(query)
        self.assertEqual(Address.inflate(res[0][0]).object_uuid,
                         response.data['id'])
        query = 'MATCH (a:Pleb)<-[:LIVES_IN]-' \
                '(b:Address {object_uuid: "%s"}) RETURN a' % (
                    response.data['object_uuid'])
        res, col = db.cypher_query(query)
        self.assertEqual(Pleb.inflate(res[0][0]).username, self.user.username)
        temp_loc.delete()
        state.delete()

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        data = {
            'city': "Walled Lake",
            'longitude': -83.48016,
            'state': "MI",
            'street': "300 Eagle Pond Dr.",
            'postal_code': "48390-3071",
            'congressional_district': "11",
            'latitude': 42.54083
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_update_no_matching_location(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        data = {
            'city': "Walled Lake",
            'longitude': -83.48016,
            'state': "MI",
            'street': "300 Eagle Pond Dr.",
            'postal_code': "48390-3071",
            'congressional_district': "100",
            'latitude': 42.54083
        }
        response = self.client.put(url, data=data, format='json')
        settings.CELERY_ALWAYS_EAGER = False
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_matching_location(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        state = Location(name="Michigan").save()
        district = Location(name="10").save()
        state.encompasses.connect(district)
        district.encompassed_by.connect(state)
        data = {
            'city': "Walled Lake",
            'longitude': -83.48016,
            'state': "MI",
            'street': "300 Eagle Pond Dr.",
            'postal_code': "48390-3071",
            'congressional_district': "10",
            'latitude': 42.54083
        }
        response = self.client.put(url, data=data, format='json')
        settings.CELERY_ALWAYS_EAGER = False
        address = Address.nodes.get(object_uuid=response.data['id'])
        self.assertIn(district, address.encompassed_by)


class ReputationMethodEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'reputation'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['reputation'], 0)

    def test_get_reputation_increase(self):
        self.client.force_authenticate(user=self.user)
        self.pleb.reputation = 10
        self.pleb.save()
        cache.clear()
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['reputation'], 10)

    def test_get_reputation_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BetaUserMethodEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'is_beta_user'
        self.email = "success@simulator.amazonses.com"
        try:
            self.pleb = Pleb.nodes.get(email=self.email)
            self.pleb.delete()
        except:
            pass
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_is_beta_user_default(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertFalse(response.data['is_beta_user'])

    def test_get_is_beta_user_true(self):
        self.client.force_authenticate(user=self.user)
        try:
            beta_user = BetaUser.nodes.get(email=self.email)
        except DoesNotExist:
            beta_user = BetaUser(email=self.email, invited=True).save()
        self.pleb.beta_user.connect(beta_user)
        self.pleb.save()
        cache.clear()
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.pleb.beta_user.disconnect(beta_user)
        self.pleb.save()
        self.assertTrue(response.data['is_beta_user'])

    def test_get_is_beta_user_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NewsfeedTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="MI",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('me-newsfeed')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_get_count(self):
        query = "match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 0)

    def test_get_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_posts(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        post = Post(content="Hey I'm a post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)

        post_two = Post(content="Hey I'm a post",
                        owner_username=self.pleb.username,
                        wall_owner_username=self.pleb.username).save()
        post_two.owned_by.connect(self.pleb)
        post_two.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post_two)
        self.pleb.posts.connect(post_two)
        post_two.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 2)

    def test_get_post_content(self):
        content = "Hey I'm a post"
        post = Post(content=content,
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'], content)

    def test_get_post_content_rendered(self):
        content = "Hey I'm a post"
        post = Post(content=content,
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_post_content_rendered_expedite(self):
        content = "Hey I'm a post"
        post = Post(content=content,
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_post_username(self):
        content = "Hey I'm a post"
        post = Post(content=content,
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         self.pleb.username)

    def test_get_quests(self):
        for update in Update.nodes.all():
            update.delete()
        for quest in Quest.nodes.all():
            quest.delete()
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 1)

    def test_get_quests_website(self):
        website = "www.sagebrew.com"
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website=website, owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['website'], website)

    def test_get_quests_rendered(self):
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_quests_rendered_expedite(self):
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_quests_title(self):
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['owner_username'],
                         self.pleb.username)

    def test_get_quest_updates(self):
        for update in Update.nodes.all():
            update.delete()
        for quest in Quest.nodes.all():
            quest.delete()
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        update = Update(content="This is a new update",
                        title="This is a title",
                        owner_username=self.pleb.username).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        update.about.connect(quest)
        quest.updates.connect(update)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 2)

    def test_get_quest_update_content(self):
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        content = "This is a new update"
        update = Update(content=content, title="This is a title",
                        owner_username=self.pleb.username).save()
        update.about.connect(quest)
        quest.updates.connect(update)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'], content)

    def test_get_quest_updates_rendered(self):
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        update = Update(content="This is a new update",
                        title="This is a title",
                        owner_username=self.pleb.username).save()
        update.quest.connect(quest)
        quest.updates.connect(update)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        print response.data
        self.assertTrue('html' in response.data['results'][0])
        self.assertTrue('html' in response.data['results'][1])

    def test_get_quest_updates_rendered_expedite(self):
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        update = Update(content="This is a new update",
                        title="This is a title",
                        owner_username=self.pleb.username).save()
        update.about.connect(quest)
        quest.updates.connect(update)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])
        self.assertTrue('html' in response.data['results'][1])

    def test_get_update_title(self):
        quest = Quest(
            active=True, about="Hey there this is my campaign. "
                               "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        mission = Mission(owner_username=quest.owner_username).save()
        quest.missions.connect(mission)
        title = "This is a title"
        update = Update(content="This is a new update",
                        title=title,
                        owner_username=self.pleb.username).save()
        update.about.connect(quest)
        quest.updates.connect(update)
        self.pleb.quest.connect(quest)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        mission.position.connect(pres)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['title'], title)

    def test_get_question_content(self):
        content = "This is the content for my question."
        question = Question(
            title=str(uuid1()),
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'], content)

    def test_get_question_title(self):
        content = "This is the content for my question."
        title = str(uuid1())
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['title'], title)

    def test_get_question_profile(self):
        content = "This is the content for my question."
        title = str(uuid1())
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         self.pleb.username)

    def test_get_question_multiple(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        content = "This is the content for my question."
        title = str(uuid1())
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        title2 = "Hello there world2"
        question_two = Question(
            title=title2,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question_two)
        question_two.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 2)

    def test_get_question_rendered(self):
        content = "This is the content for my question."
        title = str(uuid1())
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_question_rendered_expedite(self):
        content = "This is the content for my question."
        title = str(uuid1())
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_solution_content(self):
        content = 'this is fake content'
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'], content)

    def test_get_solution_profile(self):
        content = 'this is fake content'
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         self.pleb.username)

    def test_get_solution_multiple(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        content = 'this is fake content'
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)

        solution_two = Solution(content=content,
                                owner_username=self.pleb.username).save()
        solution_two.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution_two)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 2)

    def test_get_solution_rendered(self):
        content = 'this is fake content'
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_solution_rendered_expedite(self):
        content = 'this is fake content'
        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_multiple_objects(self):
        post = Post(content="Hey I'm a post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)

        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)
        self.pleb.solutions.connect(solution)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 3)

    def test_get_multiple_objects_ordering(self):
        post = Post(content="Hey I'm a post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)

        question = Question(
            title=str(uuid1()),
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)
        self.pleb.solutions.connect(solution)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        # This assumes that the above ordering creates the post first,
        # then the question, then the solution. The newsfeed should order
        # these in reverse based on their date created.
        self.assertEqual(response.data['results'][0]['type'], 'solution')
        self.assertEqual(response.data['results'][1]['type'], 'question')
        self.assertEqual(response.data['results'][2]['type'], 'post')


class TestFollowNewsfeed(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)
        rel = self.pleb.following.connect(self.pleb2)
        rel.save()
        self.question = Question(
            title=str(uuid1()),
            content="This is some arbitrary test content"
        ).save()
        self.question.owned_by.connect(self.pleb2)
        self.pleb2.questions.connect(self.question)

    def test_get_question_from_following(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'],
                         self.question.object_uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question.delete()

    def test_get_solution_from_following(self):
        self.client.force_authenticate(user=self.user)
        solution = Solution(content="Some arbitrary solution content").save()
        self.question.solutions.connect(solution)
        solution.solution_to.connect(self.question)
        self.pleb.solutions.connect(solution)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['id'],
                         solution.object_uuid)
        self.question.delete()
        solution.delete()


class TestFollowEndpoints(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.pleb2 = Pleb(username=shortuuid.uuid()).save()

    def test_follow(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-follow',
                      kwargs={'username': self.pleb2.username})
        response = self.client.post(url)
        self.assertEqual(response.data['detail'], "Successfully followed user.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_follow_already_following(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-follow',
                      kwargs={'username': self.pleb2.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['detail'], "Already following user.")

    def test_unfollow(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-unfollow',
                      kwargs={'username': self.pleb2.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Already not following user.")

    def test_unfollow_following(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-follow',
                      kwargs={'username': self.pleb2.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse('profile-unfollow',
                      kwargs={'username': self.pleb2.username})
        response = self.client.post(url)
        self.assertEqual(response.data['detail'],
                         "Successfully unfollowed user.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAcceptFriendRequest(APITestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_unauthorized(self):
        data = {}
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        data = {'this': ['This field is required.']}
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_accept_success(self):
        self.client.force_authenticate(user=self.user)
        friend_request = FriendRequest().save()
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': friend_request.object_uuid})
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.object_uuid,
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_received.connect(friend_request)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'],
                         "Successfully accepted friend request.")

    def test_accept_non_existent_request(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'request_id': str(uuid1()),
        }
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],
                         'Sorry this object does not exist.')


class TestDeclineFriendRequest(APITestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_unauthorized(self):
        data = {}
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        data = {'this': ['This field is required.']}
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_success(self):
        self.client.force_authenticate(user=self.user)
        friend_request = FriendRequest().save()
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': friend_request.object_uuid})
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.object_uuid,
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_received.connect(friend_request)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'],
                         "Successfully declined friend request.")

    def test_decline_non_existent_request(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'request_id': str(uuid1()),
        }
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],
                         'Sorry this object does not exist.')


class TestBlockFriendRequest(APITestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_unauthorized(self):
        data = {}
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        data = {'this': ['This field is required.']}
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_block_success(self):
        self.client.force_authenticate(user=self.user)
        friend_request = FriendRequest().save()
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': friend_request.object_uuid})
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.object_uuid,
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_received.connect(friend_request)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'],
                         "Successfully blocked further friend requests.")

    def test_block_non_existent_request(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'request_id': str(uuid1()),
        }
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],
                         'Sorry this object does not exist.')
