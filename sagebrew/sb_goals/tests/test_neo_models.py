from uuid import uuid1
import datetime

from django.test import TestCase

from sb_campaigns.neo_models import PoliticalCampaign
from sb_goals.neo_models import Goal, Round
from sb_donations.neo_models import Donation
from sb_updates.neo_models import Update


class TestGoalNeoModel(TestCase):
    def setUp(self):
        self.campaign = PoliticalCampaign(stripe_id=str(uuid1())).save()

    def test_create_goal(self):
        object_uuid = str(uuid1())
        goal = Goal(object_uuid=object_uuid, title="Save the world",
                    summary="I'll be saving the world by rescuing the polar"
                            "bears.",
                    description="To save the world we must save the polar"
                                "bears. This is because they are an essential"
                                "part to our day to day lives and ensure the"
                                "polar ice caps stay clean.",
                    pledged_vote_requirement=5,
                    monetary_requirement=100).save()
        goal.campaign.connect(self.campaign)
        self.campaign.goals.connect(goal)

        goal_query = Goal.nodes.get(object_uuid=object_uuid)
        self.assertEqual(goal_query.pledged_vote_requirement, 5)


class TestRoundNeoModel(TestCase):
    def setUp(self):
        self.campaign = PoliticalCampaign(stripe_id=str(uuid1())).save()
        self.round = Round(active=True).save()
        self.round.campaign.connect(self.campaign)

    def test_create_round(self):
        object_uuid = str(uuid1())
        campaign_round = Round(object_uuid=object_uuid,
                               start_date=datetime.datetime.now()).save()

        campaign_round.campaign.connect(self.campaign)
        self.campaign.rounds.connect(campaign_round)

        round_query = Round.nodes.get(object_uuid=object_uuid)
        self.assertEqual(round_query.object_uuid, object_uuid)

    def test_check_goal_completion(self):
        update = Update().save()
        goal = Goal(total_required=100, pledges_required=0, target=True).save()
        goal2 = Goal(total_required=150, pledges_required=0).save()
        donation = Donation(amount=100).save()
        self.round.goals.connect(goal)
        self.round.goals.connect(goal2)
        goal.associated_round.connect(self.round)
        goal2.associated_round.connect(self.round)
        self.round.donations.connect(donation)
        goal.updates.connect(update)
        res = self.round.check_goal_completion()
        goal.refresh()
        goal2.refresh()

        self.assertTrue(res)
        self.assertTrue(goal.completed)
        self.assertFalse(goal2.completed)

    def test_check_round_completion(self):
        upcoming_round = Round(queued=True).save()
        goal = Goal(completed=True).save()
        self.round.goals.connect(goal)
        self.campaign.active_round.connect(self.round)
        goal.associated_round.connect(self.round)

        self.campaign.upcoming_round.connect(upcoming_round)
        upcoming_round.campaign.connect(self.campaign)

        self.round.check_round_completion()

        upcoming_round.refresh()
        self.assertTrue(self.campaign.active_round.is_connected(
            upcoming_round))
        self.assertFalse(self.campaign.active_round.is_connected(self.round))
        self.assertTrue(self.round.completed)

    def test_check_round_completion_goals_not_completed(self):
        upcoming_round = Round(queued=True).save()
        goal = Goal(completed=False).save()
        self.round.goals.connect(goal)
        self.campaign.active_round.connect(self.round)
        goal.associated_round.connect(self.round)

        self.campaign.upcoming_round.connect(upcoming_round)
        upcoming_round.campaign.connect(self.campaign)

        self.round.check_round_completion()

        upcoming_round.refresh()
        self.assertFalse(self.campaign.active_round.is_connected(
            upcoming_round))
        self.assertTrue(self.campaign.active_round.is_connected(self.round))
        self.assertFalse(self.round.completed)
