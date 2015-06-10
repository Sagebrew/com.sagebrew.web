from django.core.management.base import BaseCommand

from sb_base.neo_models import VotableContent


class Command(BaseCommand):
    args = 'None.'

    def populate_owner_username(self):
        content = VotableContent.nodes.all()
        for item in content:
            if item.owner_username is None or item.owner_username == "":
                owner = item.owned_by.all()[0]
                item.owner_username = owner.username
                item.save()

    def handle(self, *args, **options):
        self.populate_owner_username()
