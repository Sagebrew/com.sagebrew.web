import stripe
from uuid import uuid1

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db
from elasticsearch import Elasticsearch, TransportError

from sb_privileges.neo_models import SBAction, Privilege
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_locations.neo_models import Location
from sb_missions.neo_models import Mission
from sb_donations.neo_models import Donation

from sb_quests.neo_models import Quest, Position
from sb_quests.serializers import QuestSerializer


class MissionEndpointTests(APITestCase):
    def setUp(self):
        query = "match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        self.unit_under_test_name = 'quest'
        self.email = "success@simulator.amazonses.com"
        self.email2 = "success2@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.user = User.objects.get(email=self.email)
        self.user2 = User.objects.get(email=self.email2)
        for camp in self.pleb.campaign.all():
            camp.delete()
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        self.mission = Mission(owner_username=self.pleb.username,
                               title=str(uuid1())).save()
        self.quest.missions.connect(self.mission)

    def test_unauthorized(self):
        url = reverse('mission-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('mission-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('mission-detail',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.post(url, data={}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_position_focus_federal_president(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "some area",
            "district": "some district",
            "level": "federal",
            "focus_name": "President"
        }
        response = self.client.post(url, data=data, format='json')
        print response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('mission-detail',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('mission-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)