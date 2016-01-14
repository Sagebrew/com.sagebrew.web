from django.core.management.base import BaseCommand

from sb_quests.neo_models import Position


class Command(BaseCommand):
    args = 'None.'

    def add_full_name_to_positions(self):
        for position in Position.nodes.all():
            full_name = Position.get_full_name(position.object_uuid)
            if full_name is not None:
                position.full_name = full_name['full_name']
                position.save()

    def handle(self, *args, **options):
        self.add_full_name_to_positions()
