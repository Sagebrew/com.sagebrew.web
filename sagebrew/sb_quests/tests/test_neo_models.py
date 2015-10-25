from uuid import uuid1

from django.test import TestCase
from django.core.cache import cache

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_donations.neo_models import Donation
from sb_goals.neo_models import Goal
from sb_quests.neo_models import Campaign, PoliticalCampaign, Position


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

    def test_get_allow_vote_user_does_not_exist(self):
        res = PoliticalCampaign.get_allow_vote(str(uuid1()), str(uuid1()))
        self.assertFalse(res)

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
