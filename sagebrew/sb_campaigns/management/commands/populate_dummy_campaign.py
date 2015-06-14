from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.cache import cache
from neomodel import db

from plebs.neo_models import Pleb

from sb_campaigns.neo_models import PoliticalCampaign, Position
from sb_donations.neo_models import PoliticalDonation
from sb_goals.neo_models import Round, Goal


class Command(BaseCommand):
    args = 'None.'

    def update_dummy_campaign(self):
        user = Pleb.nodes.all()[0]
        campaign = PoliticalCampaign(
            active=True, biography="Hey there this is my campaign. "
                                   "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=user.username,
            first_name=user.first_name, last_name=user.last_name,
            profile_pic=user.profile_pic).save()
        campaign.owned_by.connect(user)
        user.campaign.connect(campaign)
        query = "MATCH (a:Location {name: 'Michigan'})-[:POSITIONS_AVAILABLE]" \
                "->(p:Position) RETURN p"
        res, col = db.cypher_query(query)
        position = Position.inflate(res[0][0])
        campaign.position.connect(position)
        position.campaigns.connect(campaign)
        first_round = Round(start_date=datetime.now(), active=True).save()
        goal_one = Goal(
            title="This is my first goal", summary="This is a summary of my "
                                                   "very first goal.",
            description="A longer description of what I want to do if I "
                        "accomplish this goal!",
            active=True, pledged_vote_requirement=100,
            monetary_requirement=10000, total_required=10000,
            completed=True, completed_date=datetime.now()).save()
        goal_two = Goal(
            title="This is my second goal", summary="This is a summary of my "
                                                    "second goal.",
            description="A longer description of what I want to do if I "
                        "accomplish this goal and move on with my campaign!",
            active=True, pledged_vote_requirement=3400,
            monetary_requirement=20000, total_required=30000).save()
        first_round.goals.connect(goal_one)
        first_round.goals.connect(goal_two)
        goal_one.associated_round.connect(first_round)
        goal_two.associated_round.connect(first_round)
        goal_two.previous_goal.connect(goal_one)
        goal_one.next_goal.connect(goal_two)
        goal_one.campaign.connect(campaign)
        goal_two.campaign.connect(campaign)
        campaign.goals.connect(goal_one)
        campaign.goals.connect(goal_two)
        campaign.rounds.connect(first_round)
        campaign.active_round.connect(first_round)
        for value in range(0, 19):
            donation = PoliticalDonation(
                amount=500, owner_username=user.username,
                completed=True).save()
            donation.donated_for.connect(goal_one)
            donation.applied_to.connect(goal_one)
            donation.owned_by.connect(user)
            donation.campaign.connect(campaign)
            donation.associated_round.connect(first_round)
            goal_one.donations.connect(donation)
            campaign.donations.connect(donation)
            first_round.donations.connect(donation)
            user.donations.connect(donation)
        for value in range(0, 19):
            donation = PoliticalDonation(
                amount=500, owner_username=user.username).save()
            donation.donated_for.connect(goal_two)
            donation.owned_by.connect(user)
            donation.campaign.connect(campaign)
            donation.associated_round.connect(first_round)
            goal_two.donations.connect(donation)
            campaign.donations.connect(donation)
            first_round.donations.connect(donation)
            user.donations.connect(donation)
        cache.clear()

    def handle(self, *args, **options):
        self.update_dummy_campaign()
