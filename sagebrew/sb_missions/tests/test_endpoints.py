import stripe
from uuid import uuid1

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from sb_registration.utils import create_user_util_test
from sb_locations.neo_models import Location
from sb_missions.neo_models import Mission
from sb_donations.neo_models import Donation

from sb_quests.neo_models import Quest, Position


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
        usa = Location(name="United States of America").save()
        pres = Position(name="President", level="federal").save()
        usa.positions.connect(pres)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": "some district",
            "level": "federal",
            "focus_name": "President"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_federal_not_pres_no_district(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        position = Position(name="Senator", level="federal").save()
        michigan.positions.connect(position)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": "some district",
            "level": "federal",
            "focus_name": "Senator"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_federal_not_pres_district(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        d11 = Location(name="11", sector="federal").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        michigan.encompasses.connect(d11)
        d11.encompassed_by.connect(michigan)
        position = Position(name="House Representative", level="federal").save()
        d11.positions.connect(position)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": "11",
            "level": "federal",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_local(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        d11 = Location(name="Walled Lake", sector="local",
                       external_id="Walled Lake").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        michigan.encompasses.connect(d11)
        d11.encompassed_by.connect(michigan)
        position = Position(name="House Representative", level="local").save()
        d11.positions.connect(position)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Walled Lake",
            "district": "11",
            "level": "local",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_state_upper(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        position = Position(name="House Representative",
                            level="state_upper").save()
        michigan.positions.connect(position)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": None,
            "level": "state_upper",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_state_lower(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        position = Position(name="House Representative",
                            level="state_lower").save()
        michigan.positions.connect(position)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": None,
            "level": "state_lower",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_state_district(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        d11 = Location(name="11", sector="state_lower").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        michigan.encompasses.connect(d11)
        d11.encompassed_by.connect(michigan)
        position = Position(name="House Representative",
                            level="state_lower").save()
        d11.positions.connect(position)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": "11",
            "level": "state_lower",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_local(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        d11 = Location(name="Walled Lake", sector="local",
                       external_id="Walled Lake").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        michigan.encompasses.connect(d11)
        d11.encompassed_by.connect(michigan)
        position = Position(name="House Representative", level="local").save()
        d11.positions.connect(position)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Walled Lake",
            "district": "11",
            "level": "local",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_state(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan", external_id="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Michigan",
            "district": None,
            "level": "state",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_state_district(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan", external_id="Michigan").save()
        d11 = Location(name="11", external_id="11", sector="federal").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        michigan.encompasses.connect(d11)
        d11.encompassed_by.connect(michigan)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Michigan",
            "district": "11",
            "level": "state",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_federal_usa(self):
        self.client.force_authenticate(user=self.user)
        Location(name="United States of America").save()
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Michigan",
            "district": None,
            "level": "federal",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_federal_mich(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan", external_id="Michigan",
                            sector="federal").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Michigan",
            "district": None,
            "level": "federal",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_federal_district(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan", external_id="Michigan",
                            sector="federal").save()
        d11 = Location(name="11", external_id="11", sector="federal").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        michigan.encompasses.connect(d11)
        d11.encompassed_by.connect(michigan)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Michigan",
            "district": "11",
            "level": "federal",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username).save()
        self.quest.missions.connect(mission)
        data = {
            "epic": "This is my epic",
            "facebook": str(uuid1()),
            "linkedin": str(uuid1()),
            "youtube": str(uuid1()),
            "twitter": str(uuid1()),
            "website": str(uuid1()),
            "about": str(uuid1())
        }
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data=data, format='json')
        self.assertContains(response, data['epic'],
                            status_code=status.HTTP_200_OK)

    def test_update_take_active(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username).save()
        self.quest.missions.connect(mission)
        data = {
            "epic": "This is my epic",
            "facebook": str(uuid1()),
            "linkedin": str(uuid1()),
            "youtube": str(uuid1()),
            "twitter": str(uuid1()),
            "website": str(uuid1()),
            "active": True,
            "about": "     "
        }
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data=data, format='json')
        self.assertContains(response, data['epic'],
                            status_code=status.HTTP_200_OK)
        mission.refresh()
        self.assertTrue(mission.active)

    def test_update_take_inactive(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username,
                          active=True).save()
        self.quest.missions.connect(mission)
        data = {
            "epic": "This is my epic",
            "facebook": str(uuid1()),
            "linkedin": str(uuid1()),
            "youtube": str(uuid1()),
            "twitter": str(uuid1()),
            "website": str(uuid1()),
            "active": False
        }
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data=data, format='json')
        self.assertContains(response, data['epic'],
                            status_code=status.HTTP_200_OK)
        mission.refresh()
        self.assertFalse(mission.active)

    def test_update_website(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username,
                          active=True).save()
        self.quest.missions.connect(mission)
        data = {
            "epic": "This is my epic",
            "facebook": str(uuid1()),
            "linkedin": str(uuid1()),
            "youtube": str(uuid1()),
            "twitter": str(uuid1()),
            "website": "https://sagebrew.com/",
            "active": False
        }
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data=data, format='json')
        self.assertContains(response, data['epic'],
                            status_code=status.HTTP_200_OK)
        mission.refresh()
        self.assertFalse(mission.active)

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

    def test_donation_data(self):
        self.client.force_authenticate(user=self.user)
        donation = Donation(amount=30,
                            owner_username=self.pleb.username).save()
        donation.owned_by.connect(self.pleb)
        donation.mission.connect(self.mission)
        url = reverse('mission-donation-data',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
