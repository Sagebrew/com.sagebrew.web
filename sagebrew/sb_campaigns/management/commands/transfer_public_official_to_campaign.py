from django.conf import settings
from django.core.management.base import BaseCommand

from sb_public_official.neo_models import PublicOfficial
from sb_campaigns.neo_models import PoliticalCampaign


class Command(BaseCommand):
    args = 'None.'

    def transfer_public_official_to_campaign(self):
        for official in PublicOfficial.nodes.all():
            campaign = PoliticalCampaign(biography=official.bio,
                                         youtube=official.youtube,
                                         twitter=official.twitter,
                                         website=official.website,
                                         first_name=official.first_name,
                                         last_name=official.last_name,
                                         profile_pic=settings.STATIC_URL +
                                         "images/congress/225x275/%s.jpg"
                                         % (official.bioguideid)).save()
            campaign.public_official.connect(official)
            official.campaign.connect(campaign)

    def handle(self, *args, **options):
        self.transfer_public_official_to_campaign()
