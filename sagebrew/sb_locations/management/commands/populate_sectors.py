import us
from django.core.management.base import BaseCommand

from neomodel import DoesNotExist, db

from sb_locations.neo_models import Location


class Command(BaseCommand):
    args = "None."

    def populate_sectors(self):
        query = 'MATCH (location:Location) RETURN location'
        res, _ = db.cypher_query(query)
        for location in [Location.inflate(row[0]) for row in res]:
            if not location.sector:
                try:
                    encompassed_by = Location.nodes.get(
                        object_uuid=location.get_encompassed_by(
                            location.object_uuid)[0]).name
                except (DoesNotExist, Location.DoesNotExist, IndexError):
                    encompassed_by = None
                try:
                    int(location.name)
                    location.sector = "federal"
                except ValueError:
                    if location.name == "United States of America":
                        location.sector = "federal"
                        location.save()
                        continue
                    state = us.states.lookup(location.name)
                    if state is None:
                        location.sector = "local"
                    elif encompassed_by is not None and state is not None \
                            and encompassed_by != "United States of America":
                        location.sector = "local"
                    else:
                        location.sector = "federal"
                location.save()

    def handle(self, *args, **options):
        self.populate_sectors()
