from django.core.management.base import BaseCommand
from neomodel import cypher_query

class Command(BaseCommand):
    args = 'None.'

    def clear_neo_db(self):
        res = cypher_query("START n=node(*) MATCH n-[r?]-() DELETE r,n")
        print res

    def handle(self):
        self.clear_neo_db()
        print "neo4j DB cleared"