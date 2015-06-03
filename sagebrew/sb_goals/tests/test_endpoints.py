import pytz
from datetime import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_campaigns.neo_models import PoliticalCampaign, Position

from sb_goals.neo_models import Goal, Round


class GoalEndpointTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'goal'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.goal = Goal(initial=True, title='Test Goal',
                         summary="Test Summary",
                         description="Test Description", active=True,
                         pledged_vote_requirement=100,
                         monetary_requirement=1000, completed=False,
                         target=True, total_required=1000).save()

    def test_unauthorized(self):
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.goal.object_uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], 'goal')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_campaign(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['campaign'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_initial(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['initial'], self.goal.initial)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_title(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['title'], self.goal.title)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_summary(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['summary'], self.goal.summary)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_description(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['description'], self.goal.description)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pledged_vote_requirement(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['pledged_vote_requirement'],
                         self.goal.pledged_vote_requirement)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_monetary_requirement(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['monetary_requirement'],
                         self.goal.monetary_requirement)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_completed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertFalse(response.data['completed'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_completed_date(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['completed_date'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_updates(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['updates'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_associated_round(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['associated_round'], None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_donations(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['donations'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_previous_goal(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['previous_goal'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_next_goal(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['next_goal'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_active(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {
            'title': 'test update'
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['detail'],
                         "You cannot update a completed or active goal.")
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updated_completed(self):
        self.client.force_authenticate(user=self.user)
        self.goal.active = False
        self.goal.completed = True
        self.goal.save()
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {
            'title': 'test update'
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['detail'],
                         "You cannot update a completed or active goal.")
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_title(self):
        self.client.force_authenticate(user=self.user)
        self.goal.active = False
        self.goal.save()
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {
            'title': 'test update'
        }
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_update_summary(self):
        self.client.force_authenticate(user=self.user)
        self.goal.active = False
        self.goal.save()
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {
            'summary': 'test update'
        }
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.data['summary'], data['summary'])
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_update_description(self):
        self.client.force_authenticate(user=self.user)
        self.goal.active = False
        self.goal.save()
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {
            'description': 'test update'
        }
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.data['description'], data['description'])
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_update_pledged_vote_requirement(self):
        self.client.force_authenticate(user=self.user)
        self.goal.active = False
        self.goal.save()
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {
            'pledged_vote_requirement': 4000
        }
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.data['pledged_vote_requirement'],
                         data['pledged_vote_requirement'])
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_update_monetary_requirement(self):
        self.client.force_authenticate(user=self.user)
        self.goal.active = False
        self.goal.save()
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        data = {
            'monetary_requirement': 70000
        }
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.data['monetary_requirement'],
                         data['monetary_requirement'])
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_delete_active(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.delete(url)

        self.assertEqual(response.data['detail'],
                         "You cannot delete a completed or active goal.")
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_completed(self):
        self.client.force_authenticate(user=self.user)
        self.goal.active = False
        self.goal.completed = True
        self.goal.save()
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.delete(url)

        self.assertEqual(response.data['detail'],
                         "You cannot delete a completed or active goal.")
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        self.goal.active = False
        self.goal.save()
        url = reverse('goal-detail',
                      kwargs={'object_uuid': self.goal.object_uuid})
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)


class RoundEndpointTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'round'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.round = Round(upcoming=False, active=True,
                           start_date=datetime.now(pytz.utc)).save()

    def test_unauthorized(self):
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_active(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['active'], self.round.active)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.round.object_uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], 'round')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_campaign(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['campaign'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_start_date(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['start_date'],
                         response.data['start_date'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_completed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['completed'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_goals(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['goals'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_previous_round(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['previous_round'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_next_round(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['next_round'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.patch(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.put(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-detail',
                      kwargs={'object_uuid': self.round.object_uuid})
        response = self.client.post(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
