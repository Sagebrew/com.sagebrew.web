from uuid import uuid1

from django.test import TestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_goals.neo_models import Goal
from sb_campaigns.neo_models import Campaign
from sb_donations.neo_models import Donation


class TestDonationNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.goal = Goal(title="This is my goal",
                         summary="Hey this is required",
                         pledged_vote_requirement=10, monetary_requirement=10)
        self.goal.save()
        self.campaign = Campaign(stripe_id=str(uuid1())).save()

    def test_create_donation(self):
        donation = Donation(amount=5.0).save()
        donation.donated_for.connect(self.goal)
        self.goal.donations.connect(donation)
        donation.applied_to.connect(self.goal)
        donation.owned_by.connect(self.pleb)
        donation.campaign.connect(self.campaign)

        donation_query = Donation.nodes.get(object_uuid=donation.object_uuid)
        self.assertEqual(donation_query.amount, 5.0)
