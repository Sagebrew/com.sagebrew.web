from uuid import uuid1
import stripe

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission

from sb_volunteers.neo_models import Volunteer
from sb_volunteers.serializers import VolunteerSerializer


class VolunteerEndpointTests(APITestCase):

    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'goal'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)
        self.user2 = User.objects.get(email=self.email2)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        self.mission = Mission(owner_username=self.pleb.username,
                               title=str(uuid1()),
                               focus_name="advocacy").save()
        self.volunteer = Volunteer(activities=["get_out_the_vote"],
                                   mission_id=self.mission.object_uuid,
                                   owner_username=self.pleb2.username).save()
        self.quest.missions.connect(self.mission)
        self.volunteer.mission.connect(self.mission)
        self.volunteer.volunteer.connect(self.pleb2)

    def test_unauthorized(self):
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.get(url, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.post(url, {}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('volunteer-list',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['detail'],
                         "You are not authorized to access "
                         "this page.")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_list_owner(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-list',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.volunteer.object_uuid)

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], 'volunteer')

    def test_get_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.data['href'],
                         'http://testserver/v1/missions'
                         '/%s/volunteers/%s/' % (self.mission.object_uuid,
                                                 self.volunteer.object_uuid))

    def test_get_href_no_request(self):
        self.client.force_authenticate(user=self.user)
        serializer = VolunteerSerializer(self.volunteer).data
        self.assertEqual(serializer['href'],
                         '/v1/missions'
                         '/%s/volunteers/%s/' % (self.mission.object_uuid,
                                                 self.volunteer.object_uuid))

    def test_get_activities(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.get(url)

        self.assertIn("get_out_the_vote", response.data['activities'])

    def test_get_pleb(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['volunteer']['username'],
                         self.volunteer.owner_username)

    def test_get_mission(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.data['mission']['id'],
                         self.mission.object_uuid)

    def test_patch(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.patch(url, data={
            "activities": ["get_out_the_vote", "assist_with_an_event"]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("assist_with_an_event", response.data['activities'])

    def test_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.post(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.delete(url, data={}, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_owner(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-detail',
                      kwargs={'object_uuid': self.mission.object_uuid,
                              'volunteer_id': self.volunteer.object_uuid})
        response = self.client.delete(url, data={}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('volunteer-list',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.post(url, data={
            "activities": ["leaflet_voters", "write_letters_to_the_editor"]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("leaflet_voters", response.data['activities'])
        self.assertIn("write_letters_to_the_editor",
                      response.data['activities'])

    def test_me(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('volunteer-me',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("get_out_the_vote",
                      response.data['volunteered']['activities'])

    def test_me_none(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('volunteer-me',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['volunteered'])

    def test_expanded_data(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('volunteer-expanded-data',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.pleb2.email,
                      response.data["get_out_the_vote"][0]["email"])

    def test_expanded_data_dne(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('volunteer-expanded-data',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["get_out_the_vote"], [])
