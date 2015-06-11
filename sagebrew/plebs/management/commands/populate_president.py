from django.core.management.base import BaseCommand

from plebs.neo_models import Pleb
from sb_public_official.neo_models import PublicOfficial


class Command(BaseCommand):
    args = 'None.'

    def populate_president(self):
        pres = PublicOfficial.nodes.get(title='President')
        for pleb in Pleb.nodes.all():
            pleb.president.connect(pres)
        # we do not have term data for the president populated already,
        # it is not included in legislators-current.yaml which is where we
        # get the data
        pres.terms = 2
        pres.save()

    def handle(self, *args, **options):
        self.populate_president()
