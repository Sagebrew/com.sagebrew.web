from django.core.management.base import BaseCommand

from neomodel import db

from plebs.neo_models import Pleb


class Command(BaseCommand):

    def migrate_to_following(self):
        skip = 0
        while True:
            query = 'MATCH (profile:Pleb) RETURN profile ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for profile in [Pleb.inflate(row[0]) for row in res]:
                friend_query = 'MATCH (a:Pleb {username: "%s"})' \
                               '-[:FRIENDS_WITH]->(b:Pleb) RETURN b'
                res, _ = db.cypher_query(friend_query)
                for friend in [Pleb.inflate(row[0]) for row in res]:
                    profile.follow(friend)
                friends_query = 'MATCH (a:Pleb {username: "%s"})' \
                                '<-[:FRIENDS_WITH]-(b:Pleb) RETURN b'
                res, _ = db.cypher_query(friends_query)
                for friend in [Pleb.inflate(row[0]) for row in res]:
                    friend.follow(profile)
        self.stdout.write("completed friend migration\n", ending='')

        return True

    def handle(self, *args, **options):
        self.migrate_to_following()
