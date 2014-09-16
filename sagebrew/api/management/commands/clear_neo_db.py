from django.core.management.base import BaseCommand
from neomodel import cypher_query
from neomodel.exception import CypherException

class Command(BaseCommand):
    args = "None."

    def clear_neo_db(self):
        try:
            cypher_query("START n=node(*) MATCH n-[r?]-() DELETE r,n")
        except CypherException:
            pass

    def handle(self, *args, **options):
        self.clear_neo_db()

