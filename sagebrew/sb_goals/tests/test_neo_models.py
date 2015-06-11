from uuid import uuid1
import datetime

from django.test import TestCase

from sb_campaigns.neo_models import Campaign
from sb_goals.neo_models import Goal, Round


class TestGoalNeoModel(TestCase):
    def setUp(self):
        self.campaign = Campaign(stripe_id=str(uuid1())).save()

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
        self.campaign = Campaign(stripe_id=str(uuid1())).save()

    def test_create_round(self):
        object_uuid = str(uuid1())
        campaign_round = Round(object_uuid=object_uuid,
                               start_date=datetime.datetime.now()).save()

        campaign_round.campaign.connect(self.campaign)
        self.campaign.rounds.connect(campaign_round)

        round_query = Round.nodes.get(object_uuid=object_uuid)
        self.assertEqual(round_query.object_uuid, object_uuid)
