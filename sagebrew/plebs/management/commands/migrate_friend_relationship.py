from django.core.management.base import BaseCommand

from neomodel import db


class Command(BaseCommand):
    args = "None."

    def migrate_friend_relationship(self):
        query = 'MATCH (p:Pleb)-[r:FRIENDS_WITH]->(p2:Pleb) ' \
                'FOREACH (rel in [r]|SET rel.active = rel.currently_friends)' \
                ' RETURN r'
        res, _ = db.cypher_query(query)
        return True

    def handle(self, *args, **options):
        self.migrate_friend_relationship()
