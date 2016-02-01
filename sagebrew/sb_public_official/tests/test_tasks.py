import us
import time
import requests
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import DoesNotExist

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_locations.neo_models import Location
from sb_quests.neo_models import Position, Quest
from sb_public_official.tasks import create_and_attach_state_level_reps
from sb_public_official.neo_models import PublicOfficial


class TestCreateStateDistricts(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        self.headers = {"content-type": 'application/json; charset=utf8'}
        self.lookup_url = 'http://openstates.org/api/v1/legislators/geo/?' \
                          'lat=42.532020&long=-83.496500&apikey=' \
                          '53f7bd2a41df42c082bb2f07bd38e6aa'
        self.mi = Location(name=us.states.lookup("MI").name,
                           sector="federal").save()
        self.lower = Location(name='38', sector='state_lower').save()
        self.upper = Location(name='15', sector='state_upper').save()
        self.mi.encompasses.connect(self.lower)
        self.lower.encompassed_by.connect(self.mi)
        self.mi.encompasses.connect(self.upper)
        self.upper.encompassed_by.connect(self.mi)
        self.lower_pos = Position().save()
        self.lower.positions.connect(self.lower_pos)
        self.lower_pos.location.connect(self.lower)
        self.upper_pos = Position().save()
        self.upper.positions.connect(self.upper_pos)
        self.upper_pos.location.connect(self.upper)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False
        self.mi.delete()
        self.lower.delete()
        self.upper.delete()
        self.upper_pos.delete()
        self.lower_pos.delete()

    def test_success(self):
        response = requests.get(self.lookup_url, headers=self.headers)
        json_response = response.json()
        res = create_and_attach_state_level_reps.apply_async(
            kwargs={'rep_data': json_response})
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_rep_already_exists(self):
        try:
            official = PublicOfficial.nodes.get(bioguideid="MIL000290")
        except (PublicOfficial.DoesNotExist, DoesNotExist):
            official = PublicOfficial(bioguideid="MIL000290",
                                      first_name="Kathy",
                                      last_name="Crawford",
                                      state_district="38",
                                      state_chamber="lower",
                                      state="mi").save()
        response = requests.get(self.lookup_url, headers=self.headers)
        json_response = response.json()
        res = create_and_attach_state_level_reps.apply_async(
            kwargs={'rep_data': json_response})
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        camp = official.get_quest()
        self.assertTrue(camp in official.quest)
        official.delete()
        camp.delete()

    def test_rep_already_has_campaign(self):
        try:
            official = PublicOfficial.nodes.get(bioguideid="MIL000290")
            official.delete()
        except (PublicOfficial.DoesNotExist, DoesNotExist):
            pass
        official = PublicOfficial(bioguideid="MIL000290",
                                  first_name="Kathy",
                                  last_name="Crawford",
                                  state_district="38",
                                  state_chamber="lower",
                                  state="mi").save()
        campaign = Quest(first_name=official.first_name,
                         last_name=official.last_name).save()
        official.quest.connect(campaign)
        response = requests.get(self.lookup_url, headers=self.headers)
        json_response = response.json()
        res = create_and_attach_state_level_reps.apply_async(
            kwargs={'rep_data': json_response})
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        official.delete()
        campaign.delete()
