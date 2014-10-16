from django.core.management.base import BaseCommand
from time import sleep
from neomodel import db
from neomodel.exception import CypherException


class Command(BaseCommand):
    args = "None."

    def clear_neo_db(self):
        while(True):
            try:
                res = db.cypher_query(
                    "START n=node(*) OPTIONAL MATCH n-[r]-() DELETE r,n")
            except CypherException:
                sleep(1)
            else:
                break
        return True

    def handle(self, *args, **options):
        self.clear_neo_db()
