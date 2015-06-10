from django.core.management.base import BaseCommand

from neomodel import db


class Command(BaseCommand):
    args = 'None.'

    def clear_neo_db(self):
        db.cypher_query('match (n)-[r]-() delete n, r')

    def handle(self, *args, **options):
        self.clear_neo_db()
        print 'Cleared Neo DB'
