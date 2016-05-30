from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache

from neomodel import db

from sb_address.neo_models import Address
from sb_registration.utils import create_user_util_test
from sb_locations.neo_models import Location
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionReviewSerializer
from sb_quests.neo_models import Quest


class TestMissionReviewSerializer(TestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
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
        self.mission = Mission(owner_username=self.pleb.username,
                               title=str(uuid1()),
                               focus_name="advocacy",
                               location_name="11").save()
        self.mission.location.connect(self.d11)
        self.quest.missions.connect(self.mission)

    def test_no_request(self):
        data = {
            "review_feedback": []
        }
        res = MissionReviewSerializer(self.mission, data=data, partial=True)
        self.assertFalse(res.is_valid())
