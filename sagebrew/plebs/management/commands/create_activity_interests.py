from django.core.management.base import BaseCommand
from neomodel import UniqueProperty

from plebs.neo_models import ActivityInterest


class Command(BaseCommand):

    def create_activity_interests(self):
        valid_activities = ['volunteering', 'attending_events']
        for activity in valid_activities:
            try:
                ActivityInterest(name=activity).save()
            except UniqueProperty:
                pass

    def handle(self, *args, **options):
        self.create_activity_interests()
