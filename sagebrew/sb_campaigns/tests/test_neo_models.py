from uuid import uuid1

from django.test import TestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_donations.neo_models import Donation
from sb_goals.neo_models import Goal
from sb_campaigns.neo_models import Campaign, PoliticalCampaign


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
