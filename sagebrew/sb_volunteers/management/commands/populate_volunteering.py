from json import dumps
from logging import getLogger
from django.core.management.base import BaseCommand
from neomodel import DoesNotExist, CypherException

from sb_volunteers.neo_models import Volunteer

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'

    def populate_volunteering(self):
        volunteer_opportunities = [
            "get out the vote",
            "assist with an event",
            "leaflet voters",
            "write letters to the editor",
            "work in a campaign office",
            "table at events",
            "call voters",
            "data entry",
            "host a meeting",
            "host a fundraiser",
            "host a house party",
            "attend a house party"
        ]
        for opportunity in volunteer_opportunities:
            try:
                Volunteer.nodes.get(option=opportunity)
            except (Volunteer.DoesNotExist, DoesNotExist):
                Volunteer(option=opportunity).save()
            except (CypherException, IOError):
                logger.exception(
                    dumps(
                        {"detail": "Cypher exception, "
                                   "failed to create "
                                   "tag %s" % opportunity}))
                continue

    def handle(self, *args, **options):
        self.populate_volunteering()
