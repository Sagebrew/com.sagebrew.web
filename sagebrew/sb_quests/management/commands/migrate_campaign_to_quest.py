from django.core.management.base import BaseCommand

from neomodel import db, DoesNotExist

from sb_missions.neo_models import Mission
from sb_quests.neo_models import Quest, PoliticalCampaign


class Command(BaseCommand):
    args = 'None.'

    def migrate_campaign_to_quest(self):
        query = "MATCH (a:Campaign) RETURN a"
        res, _ = db.cypher_query(query)
        for row in res:
            campaign = PoliticalCampaign.inflate(row[0])
            try:
                Quest.nodes.get(owner_username=campaign.owner_username)
                continue
            except (DoesNotExist, Quest.DoesNotExist):
                pass
            quest = Quest(
                stripe_id=campaign.stripe_id,
                about=campaign.biography,
                stripe_customer_id=campaign.stripe_customer_id,
                stripe_subscription_id=campaign.stripe_subscription_id,
                active=campaign.active,
                facebook=campaign.facebook,
                linkedin=campaign.linkedin,
                youtube=campaign.youtube,
                twitter=campaign.twitter,
                website=campaign.website,
                wallpaper_pic=campaign.wallpaper_pic,
                profile_pic=campaign.profile_pic,
                application_fee=campaign.application_fee,
                last_four_soc=campaign.last_four_soc,
                seat_name=campaign.seat_name,
                seat_formal_name=campaign.seat_formal_name,
                first_name=campaign.first_name,
                last_name=campaign.last_name,
                owner_username=campaign.object_uuid
            ).save()

            for donation in campaign.donations.all():
                quest.donations.connect(donation)
                campaign.donations.disconnect(donation)

            for update in campaign.updates.all():
                quest.updates.connect(update)
                campaign.updates.disconnect(update)

            for editor in campaign.editors.all():
                quest.editors.connect(editor)
                campaign.editors.disconnect(editor)

            for moderator in campaign.accountants.all():
                quest.moderators.connect(moderator)
                campaign.accountants.disconnect(moderator)

            if campaign.epic != "" and campaign.epic is not None:
                mission = Mission(
                    biography=campaign.biography,
                    epic=campaign.epic,
                    facebook=campaign.facebook,
                    linkedin=campaign.linkedin,
                    youtube=campaign.youtube,
                    twitter=campaign.twitter,
                    website=campaign.website,
                    wallpaper_pic=campaign.wallpaper_pic,
                    owner_username=campaign.owner_username,
                    location_name=campaign.location_name,
                    focus_on_type="position"
                ).save()
                for goal in campaign.goals.all():
                    mission.goals.connect(goal)
                    campaign.goals.disconnect(goal)

                for position in campaign.position.all():
                    mission.position.connect(position)
                    mission.focused_on.connect(position)
                    campaign.position.disconnect(position)

                for pledged_vote in campaign.pledged_votes.all():
                    mission.pledge_votes.connect(pledged_vote)
                    campaign.pledged_votes.disconnect(pledged_vote)

            campaign.delete()

    def handle(self, *args, **options):
        self.migrate_campaign_to_quest()
