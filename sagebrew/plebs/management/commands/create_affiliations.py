from django.core.management.base import BaseCommand
from neomodel import UniqueProperty

from sagebrew.plebs.neo_models import PoliticalParty


class Command(BaseCommand):

    def create_political_party(self):
        valid_parties = ['democratic_party', 'independent_party', 'other',
                         'republican_party', 'libertarian_party', 'green_party',
                         'constitution_party']
        for party in valid_parties:
            try:
                formal_name = party.replace('_', ' ').replace('-', ' ').title()
                PoliticalParty(name=party, formal_name=formal_name).save()
            except UniqueProperty:
                pass

    def handle(self, *args, **options):
        self.create_political_party()
