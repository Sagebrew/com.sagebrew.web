import us
import json
import time
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import DoesNotExist

from sb_registration.utils import create_user_util_test
from sb_locations.neo_models import Location
from sb_quests.neo_models import Position, Quest
from sb_public_official.tasks import create_and_attach_state_level_reps
from sb_public_official.neo_models import PublicOfficial


class TestCreateStateDistricts(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.headers = {"content-type": 'application/json; charset=utf8'}
        with open("sb_public_official/tests/michigan_reps.json") as json_file:
            self.json_data = json.load(json_file)
        self.mi = Location(name=us.states.lookup("MI").name,
                           sector="federal").save()
        self.lower = Location(name='38', sector='state_lower').save()
        self.upper = Location(name='15', sector='state_upper').save()
        self.mi.encompasses.connect(self.lower)
        self.lower.encompassed_by.connect(self.mi)
        self.mi.encompasses.connect(self.upper)
        self.upper.encompassed_by.connect(self.mi)
        self.lower_pos = Position().save()
        self.lower_pos.location.connect(self.lower)
        self.upper_pos = Position().save()
        self.upper_pos.location.connect(self.upper)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False
        self.mi.delete()
        self.lower.delete()
        self.upper.delete()
        self.upper_pos.delete()
        self.lower_pos.delete()

    def test_success(self):
        res = create_and_attach_state_level_reps.apply_async(
            kwargs={'rep_data': self.json_data})
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
        res = create_and_attach_state_level_reps.apply_async(
            kwargs={'rep_data': self.json_data})
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
        res = create_and_attach_state_level_reps.apply_async(
            kwargs={'rep_data': self.json_data})
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        official.delete()
        campaign.delete()
