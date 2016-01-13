from django.core.management.base import BaseCommand

from neomodel import db, DoesNotExist

from sb_missions.neo_models import Mission
from sb_quests.neo_models import Quest, PoliticalCampaign, Position


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

            for editor in campaign.editors.all():
                quest.editors.connect(editor)
                campaign.editors.disconnect(editor)

            for moderator in campaign.accountants.all():
                quest.moderators.connect(moderator)
                campaign.accountants.disconnect(moderator)

            for public_official in campaign.public_official.all():
                public_official.quest.connect(quest)
                public_official.campaign.disconnect(campaign)
                campaign.public_official.disconnect(public_official)

            if campaign.epic != "" and campaign.epic is not None:
                website = campaign.website
                if website is None:
                    website = website
                elif "https://" in website or "http://" in website:
                    website = website
                else:
                    if website.strip() == "":
                        website = None
                    else:
                        website = "http://" + website
                mission = Mission(
                    about=campaign.biography,
                    epic=campaign.epic,
                    facebook=campaign.facebook,
                    linkedin=campaign.linkedin,
                    youtube=campaign.youtube,
                    twitter=campaign.twitter,
                    website=website,
                    wallpaper_pic=campaign.wallpaper_pic,
                    owner_username=campaign.object_uuid,
                    location_name=campaign.location_name,
                    focus_on_type="position",
                    active=campaign.active).save()

                for position in campaign.position.all():
                    mission.position.connect(position)
                    campaign.position.disconnect(position)

                query = 'MATCH (position:Position)-[:CAMPAIGNS]->' \
                        '(campaign:Campaign {object_uuid: "%s"}) ' \
                        'RETURN position' % campaign.object_uuid
                res, _ = db.cypher_query(query)
                if res.one:
                    positions = [Position.inflate(row[0]) for row in res]
                    for position in positions:
                        mission.position.connect(position)
                        position.campaigns.disconnect(campaign)

                for pledged_vote in campaign.pledged_votes.all():
                    mission.pledge_votes.connect(pledged_vote)
                    campaign.pledged_votes.disconnect(pledged_vote)

                for donation in campaign.donations.all():
                    donation.mission.connect(mission)
                    campaign.donations.disconnect(donation)

                for update in campaign.updates.all():
                    update.mission.connect(mission)
                    campaign.updates.disconnect(update)

                quest.missions.connect(mission)

    def handle(self, *args, **options):
        self.migrate_campaign_to_quest()
