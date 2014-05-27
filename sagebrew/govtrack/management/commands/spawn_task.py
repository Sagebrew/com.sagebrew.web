from django.core.management.base import BaseCommand
from django.conf import settings

# Still need to import your task

class Command(BaseCommand):
    args = 'None.'
    help = 'Test the conductor api endpoints.'

    def handle(self, *args, **options):
        # add the call to your task here and the 'pass' below can be removed
        # it's just a placeholder
        pass
