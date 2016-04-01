import stripe
import datetime
from uuid import uuid1

from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from plebs.neo_models import Pleb, Address
from api.utils import calc_stripe_application_fee
from sb_registration.utils import create_user_util_test
from sb_locations.neo_models import Location
from sb_missions.neo_models import Mission
from sb_donations.neo_models import Donation

from sb_volunteers.neo_models import Volunteer

from sb_quests.neo_models import Quest


class MissionEndpointTests(APITestCase):

    def setUp(self):
        query = "match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        self.unit_under_test_name = 'quest'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
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
        self.quest.missions.connect(self.mission)
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email2)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

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
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "level": "federal",
            "district": None,
            "focus_name": "President"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_federal_president_us(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('mission-list')
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        data = {
            "focus_on_type": "position",
            "location_name": None,
            "level": "federal",
            "district": None,
            "focus_name": "President"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_federal_not_pres_no_district(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "level": "federal",
            "district": None,
            "focus_name": "Senator"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
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
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": "11",
            "level": "federal",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
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
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Walled Lake",
            "district": "11",
            "level": "local",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_local_new_non_url_position(self):
        self.client.force_authenticate(user=self.user)
        name = ' 112@#$%^&*()_+~`1234567890-=[]\{}|;:",./<>?qwer  lsls., '
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        d11 = Location(name="Walled Lake", sector="local",
                       external_id="Walled Lake").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        michigan.encompasses.connect(d11)
        d11.encompassed_by.connect(michigan)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Walled Lake",
            "district": "11",
            "level": "local",
            "focus_name": name
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(mission.focus_name, slugify(
            name).title().replace('-', ' ').replace('_', ' '))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_with_no_quest(self):
        self.client.force_authenticate(user=self.user)
        query = 'MATCH (a:Pleb {username: "%s"})-[r:IS_WAGING]->(q:Quest) ' \
                'DELETE q, r' % self.pleb.username
        res, _ = db.cypher_query(query)
        self.quest.moderators.disconnect(self.pleb)
        self.quest.editors.disconnect(self.pleb)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": None,
            "level": "state_upper",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_create_position_focus_state_upper(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": None,
            "level": "state_upper",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_focus_state_lower(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": None,
            "level": "state_lower",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
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
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": "11",
            "level": "state_lower",
            "focus_name": "House Representative"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
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
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Walled Lake",
            "district": "11",
            "level": "local",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_local_url_unfriendly_focus(self):
        self.client.force_authenticate(user=self.user)
        name = ' 112@#$%^&*()_+~`1234567890-=[]\{}|;:",./<>?qwer  lsls., '
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan").save()
        d11 = Location(name="Walled Lake", sector="local",
                       external_id="Walled Lake").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        michigan.encompasses.connect(d11)
        d11.encompassed_by.connect(michigan)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Walled Lake",
            "district": "11",
            "level": "local",
            "focus_name": name
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(mission.focus_name, slugify(name))
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
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
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
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_federal_mich_usa(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        mich = Location(name="Michigan").save()
        usa.encompasses.connect(mich)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": "Michigan",
            "district": None,
            "level": "federal",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_advocacy_federal_usa(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        mich = Location(name="Michigan").save()
        usa.encompasses.connect(mich)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "advocacy",
            "location_name": None,
            "district": None,
            "level": "federal",
            "focus_name": "some random stuff"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
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
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_position_federal_mich(self):
        self.client.force_authenticate(user=self.user)
        usa = Location(name="United States of America").save()
        michigan = Location(name="Michigan", external_id="Michigan",
                            sector="federal").save()
        usa.encompasses.connect(michigan)
        michigan.encompassed_by.connect(usa)
        url = reverse('mission-list')
        data = {
            "focus_on_type": "position",
            "location_name": "Michigan",
            "district": None,
            "level": "federal",
            "focus_name": "King of Michigan"
        }
        response = self.client.post(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
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
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_more_than_free_allowed(self):
        self.client.force_authenticate(user=self.user)
        self.quest.account_type = "free"
        self.quest.save()
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
        response = {}
        for item in range(0, settings.FREE_MISSIONS + 1):
            response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Sorry free Quests can only "
                                                  "have 5 Missions.")

    def test_create_no_missions(self):
        self.client.force_authenticate(user=self.user)
        self.quest.account_type = "free"
        self.quest.save()
        for mission in self.quest.missions.all():
            self.quest.missions.disconnect(mission)
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
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.focus_on_type, data['focus_on_type'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_no_quest(self):
        self.client.force_authenticate(user=self.user)
        self.quest.owner_username = "what the ****"
        self.quest.save()
        for mission in self.quest.missions.all():
            self.quest.missions.disconnect(mission)
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "We couldn't find a Quest "
                                                  "for this Mission. Please "
                                                  "contact us if this "
                                                  "problem continues.")

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
        print(response.data)
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.facebook, data['facebook'])
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
        self.assertEqual(mission.website, data['website'])
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
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_affect_me(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?affects=me" % reverse('mission-list')
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_affect_friends(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?affects=friends" % reverse('mission-list')
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(len(response.data), 1)
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

    def test_donation_data_no_donations(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('mission-donation-data',
                      kwargs={'object_uuid': self.mission.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, '\r\n')

    def test_donation_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "amount": 500,
            "payment_method": None
        }
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        self.pleb.stripe_default_card_id = token['id']
        self.pleb.save()
        quest_token = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email
        )
        self.quest.stripe_id = quest_token['id']
        self.quest.save()
        response = self.client.post(url, data=data, format='json')
        donation = Donation.nodes.get(object_uuid=response.data['id'])
        stripe_charge = stripe.Charge.retrieve(donation.stripe_charge_id)
        application_fee = stripe.ApplicationFee.retrieve(
            stripe_charge['application_fee'])
        self.assertEqual(application_fee['amount'],
                         int((donation.amount *
                              (self.quest.application_fee +
                               settings.STRIPE_TRANSACTION_PERCENT)) + 30))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donation_create_verify_stripe_amount(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "amount": 500,
            "payment_method": None
        }
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        self.pleb.stripe_default_card_id = token['id']
        self.pleb.save()
        quest_token = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email
        )
        self.quest.stripe_id = quest_token['id']
        self.quest.save()
        response = self.client.post(url, data=data, format='json')
        donation = Donation.nodes.get(object_uuid=response.data['id'])
        stripe_charge = stripe.Charge.retrieve(donation.stripe_charge_id)
        application_fee = stripe.ApplicationFee.retrieve(
            stripe_charge['application_fee'])
        self.assertEqual(application_fee['amount'],
                         int((donation.amount *
                              (self.quest.application_fee +
                               settings.STRIPE_TRANSACTION_PERCENT)) + 30))
        self.assertEqual(stripe_charge['amount'], donation.amount)
        self.assertEqual(
            (stripe_charge['amount'] -
             calc_stripe_application_fee(stripe_charge['amount'],
                                         settings.STRIPE_FREE_ACCOUNT_FEE)),
            (donation.amount -
             calc_stripe_application_fee(donation.amount,
                                         settings.STRIPE_FREE_ACCOUNT_FEE))
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donation_create_less_than_1(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "amount": 0,
            "payment_method": None
        }
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        self.pleb.stripe_default_card_id = token['id']
        self.pleb.save()
        quest_token = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email
        )
        self.quest.stripe_id = quest_token['id']
        self.quest.save()
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_donation_create_negative(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "amount": -100,
            "payment_method": None
        }
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        self.pleb.stripe_default_card_id = token['id']
        self.pleb.save()
        quest_token = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email
        )
        self.quest.stripe_id = quest_token['id']
        self.quest.save()
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_donation_create_not_default_payment(self):
        self.client.force_authenticate(user=self.user)
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        data = {
            "amount": 700,
            "payment_method": token['id']
        }
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        quest_token = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email
        )
        self.quest.stripe_id = quest_token['id']
        self.quest.save()
        response = self.client.post(url, data=data, format='json')
        donation = Donation.nodes.get(object_uuid=response.data['id'])
        stripe_charge = stripe.Charge.retrieve(donation.stripe_charge_id)
        application_fee = stripe.ApplicationFee.retrieve(
            stripe_charge['application_fee'])
        self.assertEqual(donation.amount, data['amount'])
        self.assertEqual(application_fee['amount'],
                         int((donation.amount *
                              (self.quest.application_fee +
                               settings.STRIPE_TRANSACTION_PERCENT)) + 30))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donation_create_no_mission_title(self):
        self.client.force_authenticate(user=self.user)
        self.mission.title = ""
        self.mission.save()
        cache.clear()
        data = {
            "amount": 1500,
            "payment_method": None
        }
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        self.pleb.stripe_default_card_id = token['id']
        self.pleb.save()
        quest_token = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email
        )
        self.quest.stripe_id = quest_token['id']
        self.quest.save()
        response = self.client.post(url, data=data, format='json')
        donation = Donation.nodes.get(object_uuid=response.data['id'])
        stripe_charge = stripe.Charge.retrieve(donation.stripe_charge_id)
        application_fee = stripe.ApplicationFee.retrieve(
            stripe_charge['application_fee'])
        self.assertEqual(donation.amount, data['amount'])
        self.assertEqual(application_fee['amount'],
                         int((donation.amount *
                              (self.quest.application_fee +
                               settings.STRIPE_TRANSACTION_PERCENT)) + 30))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donation_create_quest_title(self):
        self.client.force_authenticate(user=self.user)
        self.quest.title = "This is my test Quest"
        self.quest.save()
        cache.clear()
        data = {
            "amount": 500,
            "payment_method": None
        }
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        self.pleb.stripe_default_card_id = token['id']
        self.pleb.save()
        quest_token = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email
        )
        self.quest.stripe_id = quest_token['id']
        self.quest.save()
        response = self.client.post(url, data=data, format='json')
        donation = Donation.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(donation.amount, data['amount'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donation_get(self):
        donation = Donation(amount=300).save()
        donation.mission.connect(self.mission)
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(donation.object_uuid,
                         response.data['results'][0]['id'])

    def test_donation_get_unauthorized(self):
        donation = Donation(amount=300).save()
        donation.mission.connect(self.mission)
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.quest.moderators.disconnect(self.pleb)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-list',
                      kwargs={'object_uuid': self.mission.object_uuid}) + \
            '?about_type=mission'
        data = {
            'title': str(uuid1()),
            'content': str(uuid1()),
            'about_type': 'mission',
            'about_id': self.mission.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['title'], response.data['title'])

    def test_volunteer_export(self):
        self.client.force_authenticate(user=self.user)
        volunteer = Volunteer(activities=["get_out_the_vote"],
                              mission_id=self.mission.object_uuid,
                              owner_username=self.pleb2.username).save()
        volunteer.mission.connect(self.mission)
        volunteer.volunteer.connect(self.pleb2)
        address = Address(city="Walled Lake", state="Michigan").save()
        address.owned_by.connect(self.pleb2)
        url = "/v1/missions/%s/volunteer_data/" % self.mission.object_uuid
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("test,test,bounce@simulator.amazonses.com,"
                      "Walled Lake,Michigan,x,,,,,,,,,,,", response.content)

    def test_volunteer_export_dne(self):
        self.client.force_authenticate(user=self.user)
        self.volunteer = Volunteer(activities=["get_out_the_vote"],
                                   mission_id=self.mission.object_uuid,
                                   owner_username=self.pleb2.username).save()
        self.volunteer.mission.connect(self.mission)
        self.volunteer.volunteer.connect(self.pleb2)
        url = "/v1/missions/%s/volunteer_data/" % str(uuid1())
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_volunteer_export_no_volunteers(self):
        self.client.force_authenticate(user=self.user)
        url = "/v1/missions/%s/volunteer_data/" % self.mission.object_uuid
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, 'First Name,Last Name,Email,'
                                           'City,State,Get Out '
                                           'The Vote,Assist With An Event,'
                                           'Leaflet Voters,Write Letters To '
                                           'The Editor,Work In A Campaign '
                                           'Office,Table At Events,Call Voters,'
                                           'Data Entry,Host A Meeting,Host A '
                                           'Fundraiser,Host A House Party,'
                                           'Attend A House Party\r\n')

    def test_endorse(self):
        self.client.force_authenticate(user=self.user)
        url = "/v1/missions/%s/endorse/" % self.mission.object_uuid
        response = self.client.post(url, data={"endorse_as": "profile"},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.pleb in self.mission.profile_endorsements)

    def test_unendorse(self):
        self.client.force_authenticate(user=self.user)
        url = "/v1/missions/%s/unendorse/" % self.mission.object_uuid
        response = self.client.post(url, data={"endorse_as": "profile"},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.pleb in self.mission.profile_endorsements)

    def test_endorsements(self):
        self.client.force_authenticate(user=self.user)
        self.mission.profile_endorsements.connect(self.pleb)
        url = "/v1/missions/%s/endorsements/" % self.mission.object_uuid
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'][0]['id'], self.pleb.username)

    def test_endorsements_quest(self):
        self.client.force_authenticate(user=self.user)
        self.mission.quest_endorsements.connect(self.quest)
        url = "/v1/missions/%s/endorsements/" % self.mission.object_uuid
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'][0]['id'], self.quest.object_uuid)
