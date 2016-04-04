from django.core.management.base import BaseCommand

from neomodel import db


class Command(BaseCommand):
    args = 'None.'

    def clear_neo_db(self):
        db.cypher_query('MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n, r')

    def handle(self, *args, **options):
        self.clear_neo_db()
