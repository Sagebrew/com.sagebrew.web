from django.core.management.base import BaseCommand
from neomodel import cypher_query

class Command(BaseCommand):
    def clear_neo_db(self):
        cypher_query("START n=node(*) MATCH n-[r?]-() DELETE r,n")

    def handle(self, *args, **options):
        self.clear_neo_db()