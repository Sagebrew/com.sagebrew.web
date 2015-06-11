from django.core.management.base import BaseCommand

from neomodel import db


class Command(BaseCommand):
    args = 'None.'

    def update_rep_districts(self):
        query = 'MATCH (p:PublicOfficial) WHERE ' \
                'p.title<>"Sen." AND p.district=0 FOREACH ' \
                '(n in [p]| SET p.district=1)'
        db.cypher_query(query)

    def handle(self, *args, **options):
        self.update_rep_districts()
