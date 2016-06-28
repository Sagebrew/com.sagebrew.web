from django.core.cache import cache
from django.core.management.base import BaseCommand

from googleplaces import GooglePlaces

from sb_missions.neo_models import Mission
from sb_locations.serializers import LocationSerializer


class Command(BaseCommand):
    args = 'None.'

    def add_formatted_location_name(self):
        for mission in Mission.nodes.all():
            if mission.formatted_location_name is None:
                location = mission.get_location()
                if location is not None:
                    serialized = LocationSerializer(location).data
                    google_places = GooglePlaces(
                        "AIzaSyDYSN_Flb7jJVswYVf-9pG4UMBPId3zlys")
                    place = google_places.get_place(
                        place_id=serialized['external_id'])
                    mission.formatted_location_name = place.formatted_address
                    mission.save()
        cache.set("add_formatted_location_names", True)

    def handle(self, *args, **options):
        if not cache.get("add_formatted_location_names"):
            self.add_formatted_location_name()
