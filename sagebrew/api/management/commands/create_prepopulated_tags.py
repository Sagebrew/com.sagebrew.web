from django.core.management.base import BaseCommand
from django.conf import settings

from neomodel import DoesNotExist

from sb_tag.neo_models import SBTag


class Command(BaseCommand):
    args = 'None.'

    def populate_base_tags(self):
        for tag in settings.BASE_TAGS:
            try:
                SBTag.nodes.get(tag_name=tag)
            except (SBTag.DoesNotExist, DoesNotExist):
                SBTag(tag_name=tag, base=True).save()

    def handle(self, *args, **options):
        self.populate_base_tags()