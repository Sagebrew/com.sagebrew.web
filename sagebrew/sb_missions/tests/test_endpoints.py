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

from neomodel import db, DoesNotExist

from plebs.neo_models import Pleb
from sb_address.neo_models import Address
from api.utils import calc_stripe_application_fee
from sb_registration.utils import create_user_util_test
from sb_locations.neo_models import Location
from sb_missions.neo_models import Mission
from sb_donations.neo_models import Donation
from sb_volunteers.neo_models import Volunteer
from sb_quests.neo_models import Quest


class MissionEndpointTests(APITestCase):

    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        cache.clear()
        self.unit_under_test_name = 'quest'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        self.usa = Location(name="United States of America").save()
        self.michigan = Location(name="Michigan").save()
        self.d11 = Location(name="11", sector="federal").save()
        self.usa.encompasses.connect(self.michigan)
        self.michigan.encompassed_by.connect(self.usa)
        self.michigan.encompasses.connect(self.d11)
        self.d11.encompassed_by.connect(self.michigan)
        self.address = Address(
            street="125 Glenwood Drive",
            city="Walled Lake", state="Michigan",
            postal_code="48390",
            country="USA", county="Oakland",
            congressional_district=11, validated=True).save()
        self.address.encompassed_by.connect(self.d11)
        self.quest.address.connect(self.address)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        self.mission = Mission(owner_username=self.pleb.username,
                               title=str(uuid1()),
                               focus_name="advocacy",
                               location_name="11").save()
        self.mission.location.connect(self.d11)
        self.quest.missions.connect(self.mission)
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)
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
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "about": str(uuid1())
        }
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(mission.facebook, data['facebook'])

    def test_update_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        mission_old = Mission(title=str(uuid1()),
                              owner_username=self.pleb.username).save()
        self.quest.missions.connect(mission_old)
        data = {
            "epic": "Fake epic content that was made by a fake user",
        }
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission_old.object_uuid})
        response = self.client.patch(url, data=data, format='json')
        mission = Mission.nodes.get(object_uuid=mission_old.object_uuid)
        self.assertEqual(mission.epic, mission_old.epic)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Only the owner can edit this'])

    def test_update_epic_with_h3_first(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username).save()

        self.quest.missions.connect(mission)
        content = "<h3> hello world this is a h3 </h3>\n" \
                  "<h2> with a h2 after it </h2>\n" \
                  "<h3> another h3 </h3>\n" \
                  "and then some text"
        data = {
            "epic": content,
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "about": str(uuid1())
        }
        content = '<h3 style="padding-top: 0; margin-top: 5px;"> ' \
                  'hello world this is a h3 </h3>\n' \
                  '<h2> with a h2 after it </h2>\n' \
                  '<h3> another h3 </h3>\n' \
                  'and then some text'
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['epic'], content)

    def test_update_epic_with_h2_first(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username).save()

        self.quest.missions.connect(mission)
        content = "<h2> hello world this is a h2 </h2>\n" \
                  "<h1> with a h1 after it </h1>\n" \
                  "<h2> another h2 </h2>\n" \
                  "and then some text"
        data = {
            "epic": content,
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "about": str(uuid1())
        }
        content = '<h2 style="padding-top: 0; margin-top: 5px;"> ' \
                  'hello world this is a h2 </h2>\n' \
                  '<h1> with a h1 after it </h1>\n' \
                  '<h2> another h2 </h2>\n' \
                  'and then some text'
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['epic'], content)

    def test_update_website(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username,
                          active=True).save()
        self.quest.missions.connect(mission)
        data = {
            "epic": "This is my epic",
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "active": False
        }
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data=data, format='json')
        self.assertContains(response, data['epic'],
                            status_code=status.HTTP_200_OK)
        mission.refresh()
        self.assertEqual(mission.website, data['website'])

    def test_update_temp_epic(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username,
                          active=True,
                          temp_epic="this is a temp epic").save()
        self.quest.missions.connect(mission)
        data = {
            "temp_epic": "<p>%s</p>" % str(uuid1())
        }
        url = reverse('mission-detail',
                      kwargs={'object_uuid': mission.object_uuid})
        response = self.client.patch(url, data=data, format='json')
        self.assertContains(response, data['temp_epic'],
                            status_code=status.HTTP_200_OK)
        mission.refresh()
        self.assertEqual(mission.temp_epic, data['temp_epic'])

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
        mission2 = Mission(owner_username=self.pleb.username,
                           title=str(uuid1()),
                           focus_name="advocacy",
                           location_name="12").save()
        d12 = Location(name="12", sector="state_lower").save()
        d12.encompassed_by.connect(self.michigan)
        mission2.location.connect(d12)
        self.quest.missions.connect(self.mission)
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_affect_friends(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?affects=friends" % reverse('mission-list')
        response = self.client.get(url, format='json')
        mission2 = Mission(owner_username=self.pleb.username,
                           title=str(uuid1()),
                           focus_name="advocacy",
                           location_name="12").save()
        mission3 = Mission(owner_username=self.pleb.username,
                           title=str(uuid1()),
                           focus_name="advocacy",
                           location_name="13").save()
        address = Address(
            street="3295 Rio Vista St",
            city="Commerce Township", state="Michigan",
            postal_code="48382",
            country="USA", county="Oakland",
            congressional_district=12, validated=True).save()
        self.quest.address.connect(address)
        d12 = Location(name="12", sector="state_lower").save()
        d13 = Location(name="13", sector="state_lower").save()
        d12.encompassed_by.connect(self.michigan)
        d13.encompassed_by.connect(self.michigan)
        mission2.location.connect(d12)
        mission3.location.connect(d13)
        self.pleb.friends.connect(self.pleb2)
        self.pleb2.friends.connect(self.pleb)
        self.assertGreaterEqual(len(response.data), 2)
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
        stripe.api_version = settings.STRIPE_API_VERSION
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
        stripe.api_version = settings.STRIPE_API_VERSION
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
        stripe.api_version = settings.STRIPE_API_VERSION
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

    def test_donation_create_one_million_dollars(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "amount": 100000000,
            "payment_method": None
        }
        url = "/v1/missions/%s/donations/" % self.mission.object_uuid
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
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
        self.assertEqual(response.data,
                         {"amount": ["Donations cannot be over $999,999.99"]})
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
        stripe.api_version = settings.STRIPE_API_VERSION
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
        stripe.api_version = settings.STRIPE_API_VERSION

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
        stripe.api_version = settings.STRIPE_API_VERSION
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
        cache.clear()
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
        stripe.api_version = settings.STRIPE_API_VERSION
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
        self.pleb2.address.connect(address)
        url = "/v1/missions/%s/volunteer_data/" % self.mission.object_uuid
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("test,test,bounce@simulator.amazonses.com,"
                      "Walled Lake,Michigan,x,,,,,,,,,,,", response.content)

    def test_volunteer_no_address_export(self):
        self.client.force_authenticate(user=self.user)
        volunteer = Volunteer(activities=["get_out_the_vote"],
                              mission_id=self.mission.object_uuid,
                              owner_username=self.pleb2.username).save()
        volunteer.mission.connect(self.mission)
        volunteer.volunteer.connect(self.pleb2)
        for address in self.pleb2.address.all():
            self.pleb2.address.disconnect(address)
        url = "/v1/missions/%s/volunteer_data/" % self.mission.object_uuid
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("test,test,bounce@simulator.amazonses.com,"
                      "N/A,N/A,x,,,,,,,,,,,", response.content)

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
                                           'Attend A House Party,Other\r\n')

    def test_endorse(self):
        self.client.force_authenticate(user=self.user)
        url = "/v1/missions/%s/endorse/" % self.mission.object_uuid
        response = self.client.post(url, data={"endorse_as": "profile"},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.pleb in self.mission.profile_endorsements)

    def test_endorse_unauthorized(self):
        url = "/v1/missions/%s/endorse/" % self.mission.object_uuid
        response = self.client.post(url, data={"endorse_as": "profile"},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_reset_epic(self):
        self.client.force_authenticate(user=self.user)
        self.mission.temp_epic = "SOMETHING DIFFERENT THAN EPIC"
        self.mission.epic = "THIS IS MY EPIC!"
        self.mission.save()
        url = "/v1/missions/%s/reset_epic/" % self.mission.object_uuid
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mission = Mission.nodes.get(object_uuid=self.mission.object_uuid)
        self.assertEqual(mission.epic, mission.temp_epic)

    def test_review_mission(self):
        self.user.username = "tyler_wiersing"
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = "/v1/missions/%s/review/" % self.mission.object_uuid
        data = {
            "review_feedback": ["porn", "too_short"]
        }
        res = self.client.patch(url, data=data, format="json")
        self.mission = Mission.nodes.get(object_uuid=self.mission.object_uuid)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("porn", self.mission.review_feedback)
        self.assertIn("too_short", self.mission.review_feedback)

    def test_review_mission_take_active(self):
        self.user.username = "tyler_wiersing"
        self.user.save()
        self.client.force_authenticate(user=self.user)
        self.mission.active = False
        self.mission.save()
        url = "/v1/missions/%s/review/" % self.mission.object_uuid
        data = {
            "review_feedback": []
        }
        res = self.client.patch(url, data=data, format="json")
        self.mission = Mission.nodes.get(object_uuid=self.mission.object_uuid)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual([], self.mission.review_feedback)
        self.assertTrue(self.mission.active)

    def test_review_mission_not_authorized(self):
        self.user.username = "test_test"
        self.user.save()
        self.client.force_authenticate(user=self.user)
        self.mission.active = False
        self.mission.save()
        url = "/v1/missions/%s/review/" % self.mission.object_uuid
        data = {
            "review_feedback": []
        }
        res = self.client.patch(url, data=data, format="json")
        self.mission = Mission.nodes.get(object_uuid=self.mission.object_uuid)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.mission.active)

    def test_review_mission_invalid_data(self):
        self.user.username = "test_test"
        self.user.save()
        self.client.force_authenticate(user=self.user)
        self.mission.active = False
        self.mission.save()
        url = "/v1/missions/%s/review/" % self.mission.object_uuid
        data = {
            str(uuid1()): []
        }
        res = self.client.patch(url, data=data, format="json")
        self.mission = Mission.nodes.get(object_uuid=self.mission.object_uuid)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.mission.active)

    def test_get_submitted_for_review(self):
        self.client.force_authenticate(user=self.user)
        self.mission.submitted_for_review = True
        self.mission.save()
        cache.clear()
        url = "/v1/missions/?submitted_for_review=true&active=false"
        res = self.client.get(url)
        self.assertEqual(res.data['results'][0]['id'], self.mission.object_uuid)
        self.mission.submitted_for_review = False
        self.mission.save()

    def test_get_submitted_for_review_active(self):
        self.client.force_authenticate(user=self.user)
        self.mission.submitted_for_review = True
        self.mission.active = True
        self.mission.save()
        cache.clear()
        url = "/v1/missions/?submitted_for_review=true&active=true"
        res = self.client.get(url)
        self.assertEqual(res.data['results'][0]['id'], self.mission.object_uuid)
        self.mission.submitted_for_review = False
        self.mission.active = False
        self.mission.save()

    def test_submit_for_review(self):
        try:
            pleb2 = Pleb.nodes.get(username=settings.INTERCOM_USER_ID_DEVON)
        except (Pleb.DoesNotExist, DoesNotExist):
            pleb2 = Pleb(username=settings.INTERCOM_USER_ID_DEVON).save()
        self.client.force_authenticate(user=self.user)
        self.mission.submitted_for_review = False
        self.mission.save()
        cache.clear()
        url = "/v1/missions/%s/" % self.mission.object_uuid
        data = {
            "submitted_for_review": True
        }
        res = self.client.patch(url, data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['submitted_for_review'])
        pleb2.delete()
        cache.clear()

    def test_update_epic_with_problems(self):
        try:
            pleb2 = Pleb.nodes.get(username=settings.INTERCOM_USER_ID_DEVON)
        except (Pleb.DoesNotExist, DoesNotExist):
            pleb2 = Pleb(username=settings.INTERCOM_USER_ID_DEVON).save()
        self.client.force_authenticate(user=self.user)
        self.mission.submitted_for_review = True
        self.mission.review_feedback = ['too_short']
        self.mission.active = False
        self.mission.save()
        cache.clear()
        url = "/v1/missions/%s/" % self.mission.object_uuid
        data = {
            "epic": "<p>This is an epic update!</p>"
        }
        res = self.client.patch(url, data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['epic'], data['epic'])
        pleb2.delete()
        cache.clear()
