from django.core.management.base import BaseCommand
from neomodel import db
from neomodel.exception import CypherException

class Command(BaseCommand):
    args = "None."

    def clear_neo_db(self):
        try:
            db.cypher_query("START n=node(*) OPTIONAL MATCH n-[r]-() DELETE r,n")
        except CypherException:
            pass

    def handle(self, *args, **options):
        self.clear_neo_db()

