from django.core.management.base import BaseCommand

from neomodel import db

from sagebrew.plebs.neo_models import Pleb


class Command(BaseCommand):

    def migrate_to_following(self):
        skip = 0
        while True:
            query = 'MATCH (profile:Pleb) RETURN profile ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res[0] if res else None:
                break
            for profile in [Pleb.inflate(row[0]) for row in res]:
                friend_query = 'MATCH (a:Pleb {username: "%s"})' \
                               '-[:FRIENDS_WITH]->(b:Pleb) ' \
                               'RETURN b' % profile.username
                friend_res, _ = db.cypher_query(friend_query)
                for friend in [Pleb.inflate(friend_row[0])
                               for friend_row in friend_res]:
                    try:
                        profile.follow(friend.username)
                        friend.follow(profile.username)
                    except Exception:
                        pass
        self.stdout.write("completed friend migration\n", ending='')

        return True

    def handle(self, *args, **options):
        self.migrate_to_following()
