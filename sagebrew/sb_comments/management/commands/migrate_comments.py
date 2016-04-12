from django.core.management.base import BaseCommand

from neomodel import db


class Command(BaseCommand):
    args = 'None.'

    def migrate_comments(self):
        query = 'MATCH (a:Comment)<-[:HAS_A]-(b:SBContent) ' \
                'SET a.parent_id=b.object_uuid RETURN a'
        db.cypher_query(query)
        self.stdout.write("completed comment migration\n", ending='')

    def handle(self, *args, **options):
        self.migrate_comments()
