from django.test import TestCase

from sb_campaigns.neo_models import PoliticalCampaign

from sb_goals.neo_models import Goal, Round
from sb_goals.serializers import RoundSerializer


class TestRoundSerializer(TestCase):
    def setUp(self):
        self.campaign = PoliticalCampaign(active=True).save()
        self.round = Round(active=True).save()
        self.round2 = Round(queued=True).save()
        self.round.next_round.connect(self.round2)
        self.round2.previous_round.connect(self.round)
        self.campaign.active_round.connect(self.round)
        self.campaign.upcoming_round.connect(self.round2)
        self.campaign.rounds.connect(self.round)
        self.round2.campaign.connect(self.campaign)
        self.round.campaign.connect(self.campaign)
        self.goal1 = Goal(total_required=100, active=True, target=True).save()
        self.goal2 = Goal(total_required=200, active=True).save()
        self.goal1.next_goal.connect(self.goal2)
        self.goal2.previous_goal.connect(self.goal1)
        self.goal3 = Goal(total_required=100, active=False).save()

    def test_swap_active_and_upcoming(self):
        self.campaign.active_round.disconnect(self.round)
        serializer = RoundSerializer(instance=self.round2).update(
            instance=self.round2, validated_data={})

        self.assertTrue(len(self.campaign.active_round.all()), 1)
        self.assertTrue(self.campaign.active_round.is_connected(serializer))
