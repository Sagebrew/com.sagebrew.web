from django.core.management.base import BaseCommand
from neomodel import db
from neomodel.exception import CypherException


class Command(BaseCommand):
    args = "None."

    def clear_neo_db(self):
        try:
            res = db.cypher_query(
                "START n=node(*) OPTIONAL MATCH n-[r]-() DELETE r,n")
        except CypherException:
            try:
                res = db.cypher_query(
                    "START n=node(*) OPTIONAL MATCH n-[r]-() DELETE r,n")
                while type(res) != tuple:
                    res = db.cypher_query(
                        "START n=node(*) OPTIONAL MATCH n-[r]-() DELETE r,n")
            except CypherException:
                return False
        return True

    def handle(self, *args, **options):
        self.clear_neo_db()
