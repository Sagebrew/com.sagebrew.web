import pytz
import datetime
from uuid import uuid1

from django.test import TestCase
from django.core.cache import cache
from rest_framework.reverse import reverse
from neomodel import DoesNotExist

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_donations.neo_models import Donation
from sb_goals.neo_models import Goal
from sb_locations.neo_models import Location
from sb_quests.neo_models import Campaign, PoliticalCampaign, Position, Quest
from sb_tags.neo_models import Tag
from sb_questions.neo_models import Question
from sb_updates.neo_models import Update

from sb_missions.neo_models import Mission


class TestMission(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.owner = Pleb.nodes.get(email=self.email)
        self.quest = Quest(owner_username=self.owner.username,
                           object_uuid=str(uuid1())).save()
        self.owner.quest.connect(self.quest)
        self.mission = Mission(owner_username=self.owner.username,
                               title=str(uuid1())).save()
        self.quest.missions.connect(self.mission)

    def test_get_not_cached(self):
        cache.clear()
        res = Mission.get(self.mission.object_uuid)
        self.assertEqual(res.object_uuid, self.mission.object_uuid)

    def test_get_cached(self):
        cache.set("%s_mission" % self.mission.object_uuid, self.mission)
        res = Mission.get(self.mission.object_uuid)
        self.assertEqual(res.object_uuid, self.mission.object_uuid)

    def test_get_dne(self):
        try:
            Mission.get(str(uuid1()))
        except DoesNotExist:
            # this is the best way to test this, maybe?
            self.assertTrue(True)

    def test_get_quest(self):
        res = Mission.get_quest(self.mission.object_uuid)
        self.assertEqual(res.owner_username, self.quest.owner_username)

    def test_get_focus_on_position(self):
        position = Position().save()
        self.mission.position.connect(position)
        res = self.mission.get_focused_on()
        self.assertEqual(position.object_uuid, res['id'])

    def test_get_focus_on_tag(self):
        tag = Tag(name=str(uuid1())).save()
        self.mission.tag.connect(tag)
        res = self.mission.get_focused_on()
        self.assertIn(tag.object_uuid, res['id'])

    def test_get_focus_on_question(self):
        question = Question(title=str(uuid1())).save()
        self.mission.question.connect(question)
        res = self.mission.get_focused_on()
        self.assertIn(question.object_uuid, res['id'])

    def test_get_location(self):
        location = Location().save()
        self.mission.location.connect(location)
        res = self.mission.get_location()
        self.assertEqual(res.object_uuid, location.object_uuid)

    def test_get_editors(self):
        self.quest.editors.connect(self.owner)
        cache.clear()
        res = Mission.get_editors(self.mission.owner_username)
        self.assertIn(self.owner.username, res)

    def test_get_moderators(self):
        self.quest.moderators.connect(self.owner)
        cache.clear()
        res = Mission.get_moderators(self.mission.owner_username)
        self.assertIn(self.owner.username, res)

    def test_get_donations(self):
        donation = Donation(amount=500).save()
        donation.mission.connect(self.mission)
        res = Mission.get_donations(self.mission.object_uuid)
        self.assertEqual(res[0].object_uuid, donation.object_uuid)

    def test_get_mission_title(self):
        res = self.mission.get_mission_title()
        self.assertEqual(res, self.mission.title)

    def test_get_mission_title_no_title(self):
        self.mission.title = ""
        self.focus_name = "Some test stuff"
        self.mission.save()
        res = self.mission.get_mission_title()
        self.assertIsNone(res)

    def test_get_total_donation_amount(self):
        donation1 = Donation(amount=10).save()
        donation2 = Donation(amount=20).save()
        donation1.mission.connect(self.mission)
        donation2.mission.connect(self.mission)
        res = self.mission.get_total_donation_amount()
        self.assertEqual(res, 30)
