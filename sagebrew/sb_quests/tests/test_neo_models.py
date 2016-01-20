import pytz
import datetime
from uuid import uuid1

from django.test import TestCase
from django.core.cache import cache
from rest_framework.reverse import reverse

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_donations.neo_models import Donation
from sb_goals.neo_models import Goal
from sb_locations.neo_models import Location
from sb_quests.neo_models import Campaign, PoliticalCampaign, Position, Quest
from sb_updates.neo_models import Update
from sb_missions.neo_models import Mission


class TestCampaignNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.campaigner = Pleb.nodes.get(email=self.email)
        self.goal = Goal(title="This is my goal",
                         summary="Hey this is required",
                         pledged_vote_requirement=10, monetary_requirement=10)
        self.goal.save()
        self.donation = Donation(amount=5.0).save()

    def test_create_campaign(self):
        stripe_id = str(uuid1())
        campaign = Campaign(stripe_id=stripe_id).save()
        campaign.donations.connect(self.donation)
        self.donation.campaign.connect(campaign)
        campaign.goals.connect(self.goal)
        campaign.owned_by.connect(self.campaigner)
        self.goal.campaign.connect(campaign)

        campaign_query = Campaign.nodes.get(stripe_id=stripe_id)
        self.assertEqual(campaign_query.stripe_id, stripe_id)


class TestPoliticalCampaignNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.campaigner = Pleb.nodes.get(email=self.email)
        self.donation = Donation(amount=5.0).save()
        self.campaign = PoliticalCampaign().save()

    def test_get_allow_vote_user_does_not_exist(self):
        res, detail = PoliticalCampaign.get_allow_vote(
            str(uuid1()), str(uuid1()))
        self.assertFalse(res)
        self.assertEqual(detail['detail'], 'This user does not exist.')

    def test_get_allow_vote_user_is_not_verified(self):
        self.campaigner.is_verified = False
        self.campaigner.save()
        cache.clear()
        res = PoliticalCampaign.get_allow_vote(self.campaign.object_uuid,
                                               self.campaigner.username)
        self.assertFalse(res[0])
        self.assertEqual(res[1]['detail'],
                         'You must be a verified user to pledge a vote to '
                         'a Quest.')
        self.campaigner.is_verified = True
        self.campaigner.save()

    def test_campaign_to_political_campaign(self):
        stripe_id = str(uuid1())
        campaign = PoliticalCampaign(stripe_id=stripe_id).save()
        campaign = Campaign.get(object_uuid=campaign.object_uuid)
        self.assertIs(type(campaign), Campaign)
        campaign = PoliticalCampaign.get(object_uuid=campaign.object_uuid)
        self.assertIs(type(campaign), PoliticalCampaign)
        votes = campaign.get_vote_count(object_uuid=campaign.object_uuid)
        self.assertEqual(votes, 0)

    def test_get_position_level(self):
        campaign = PoliticalCampaign().save()
        position = Position(level='federal').save()
        campaign.position.connect(position)
        position.campaigns.connect(campaign)
        res = PoliticalCampaign.get_position_level(campaign.object_uuid)
        self.assertEqual(res, position.level)

    def test_get_position_level_cached(self):
        campaign = PoliticalCampaign().save()
        position = Position(level='state_upper').save()
        cache.set("%s_position" % campaign.object_uuid, position.level)
        campaign.position.connect(position)
        position.campaigns.connect(campaign)
        res = PoliticalCampaign.get_position_level(campaign.object_uuid)
        self.assertEqual(res, position.level)

    def test_pledged_votes_per_day(self):
        campaign = PoliticalCampaign().save()
        self.campaigner.campaign.connect(campaign)
        campaign.owned_by.connect(self.campaigner)
        rel = campaign.pledged_votes.connect(self.campaigner)
        rel.active = True
        rel.save()
        res = campaign.pledged_votes_per_day()
        self.assertEqual(
            res, {rel.created.strftime('%Y-%m-%d'): int(rel.active)})

    def test_pledged_votes_per_day_multiple_votes_same_day(self):
        pleb = Pleb(username=str(uuid1())).save()
        campaign = PoliticalCampaign().save()
        self.campaigner.campaign.connect(campaign)
        campaign.owned_by.connect(self.campaigner)
        rel = campaign.pledged_votes.connect(self.campaigner)
        rel.active = True
        rel.save()
        rel2 = campaign.pledged_votes.connect(pleb)
        rel2.active = True
        rel.save()
        res = campaign.pledged_votes_per_day()
        self.assertEqual(
            res, {rel.created.strftime('%Y-%m-%d'): 2})

    def test_pledged_votes_per_day_multiple_votes_different_days(self):
        pleb = Pleb(username=str(uuid1())).save()
        campaign = PoliticalCampaign().save()
        self.campaigner.campaign.connect(campaign)
        campaign.owned_by.connect(self.campaigner)
        rel = campaign.pledged_votes.connect(self.campaigner)
        rel.active = True
        rel.save()
        rel2 = campaign.pledged_votes.connect(pleb)
        rel2.active = True
        rel2.created = datetime.datetime.now(pytz.utc) + datetime.timedelta(
            days=3)
        rel2.save()
        res = campaign.pledged_votes_per_day()
        self.assertEqual(
            res, {rel.created.strftime('%Y-%m-%d'): int(rel.active),
                  rel2.created.strftime('%Y-%m-%d'): int(rel2.active)})


class TestPosition(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.position = Position().save()

    def test_get_full_name_house_rep(self):
        self.position.name = "House Representative"
        self.position.level = "federal"
        self.position.save()
        state = Location(name="Michigan", level="federal").save()
        district = Location(name="11", level="federal").save()
        state.encompasses.connect(district)
        district.encompassed_by.connect(state)
        self.position.location.connect(district)
        district.positions.connect(self.position)
        res = Position.get_full_name(self.position.object_uuid)
        self.assertEqual(res['full_name'], "House Representative for "
                                           "Michigan's 11th district")

    def test_get_full_name_senator(self):
        self.position.name = "Senator"
        self.position.level = "federal"
        self.position.save()
        state = Location(name="Michigan", level="federal").save()
        self.position.location.connect(state)
        state.positions.connect(self.position)
        res = Position.get_full_name(self.position.object_uuid)
        self.assertEqual(res['full_name'], "Senator of Michigan")

    def test_get_full_name_state_senator(self):
        self.position.name = "State Senator"
        self.position.level = "state_upper"
        self.position.save()
        state = Location(name="Michigan", level="federal").save()
        district = Location(name="38", level="state_upper").save()
        state.encompasses.connect(district)
        district.encompassed_by.connect(state)
        self.position.location.connect(district)
        district.positions.connect(self.position)
        res = Position.get_full_name(self.position.object_uuid)
        self.assertEqual(res['full_name'], "State Senator for Michigan's "
                                           "38th district")

    def test_get_full_name_state_house_rep(self):
        self.position.name = "State House Representative"
        self.position.level = "state_lower"
        self.position.save()
        state = Location(name="Michigan", level="federal").save()
        district = Location(name="15", level="state_lower").save()
        state.encompasses.connect(district)
        district.encompassed_by.connect(state)
        self.position.location.connect(district)
        district.positions.connect(self.position)
        res = Position.get_full_name(self.position.object_uuid)
        self.assertEqual(res['full_name'], "State House Representative"
                                           " for Michigan's 15th district")


class TestQuest(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.owner = Pleb.nodes.get(email=self.email)
        self.quest = Quest(owner_username=self.owner.username,
                           object_uuid=str(uuid1())).save()
        self.owner.quest.connect(self.quest)

    def test_get_cached(self):
        cache.set("%s_quest" % self.owner.username, self.quest)
        res = Quest.get(self.owner.username)
        self.assertEqual(self.quest, res)

    def test_get_not_cached(self):
        cache.delete("%s_quest" % self.owner.username)
        res = Quest.get(self.owner.username)
        self.assertEqual(self.quest.owner_username, res.owner_username)

    def test_get_editors(self):
        self.quest.editors.connect(self.owner)
        res = Quest.get_editors(self.owner.username)
        self.assertIn(self.owner.username, res)

    def test_get_moderators(self):
        self.quest.moderators.connect(self.owner)
        res = Quest.get_moderators(self.owner.username)
        self.assertIn(self.owner.username, res)

    def test_get_quest_helpers(self):
        self.quest.editors.connect(self.owner)
        self.quest.moderators.connect(self.owner)
        res = Quest.get_quest_helpers(self.owner.username)
        self.assertIn(self.owner.username, res)

    def test_get_url(self):
        res = Quest.get_url(self.quest.object_uuid, None)
        self.assertEqual(res, reverse(
            'quest', kwargs={"username": self.owner.username}))

    def test_get_updates(self):
        update = Update().save()
        self.quest.updates.connect(update)
        cache.delete("%s_updates" % self.quest.object_uuid)
        res = Quest.get_updates(self.quest.object_uuid)
        self.assertIn(update.object_uuid, res)

    def test_get_donations(self):
        donation = Donation().save()
        mission = Mission().save()
        self.quest.missions.connect(mission)
        donation.mission.connect(mission)
        donation.quest.connect(self.quest)
        res = Quest.get_donations(self.quest.owner_username)
        self.assertEqual(donation.object_uuid, res[0].object_uuid)

    def test_is_following(self):
        self.quest.follow(self.owner.username)
        self.assertTrue(self.owner in self.quest.followers)
        res = self.quest.is_following(self.owner.username)
        self.assertTrue(res)

    def test_follow(self):
        self.quest.follow(self.owner.username)
        self.assertTrue(self.owner in self.quest.followers)

    def test_unfollow(self):
        self.quest.follow(self.owner.username)
        self.assertTrue(self.owner in self.quest.followers)
        res = self.quest.unfollow(self.owner.username)
        self.assertFalse(res)

    def test_get_followers(self):
        self.quest.follow(self.owner.username)
        self.assertTrue(self.owner in self.quest.followers)
        res = self.quest.get_followers()
        self.assertIn(self.owner.username, res)

    def test_get_total_donation_amount(self):
        donation1 = Donation(amount=10).save()
        donation2 = Donation(amount=20).save()
        donation1.quest.connect(self.quest)
        donation2.quest.connect(self.quest)
        res = self.quest.get_total_donation_amount()
        self.assertEqual(res, 30)
