from django.core.management.base import BaseCommand

from neomodel import db

from sagebrew.plebs.neo_models import Pleb


class Command(BaseCommand):

    def populate_last_reputation_node(self):
        skip = 0
        while True:
            query = 'MATCH (profile:Pleb) RETURN profile ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res[0] if res else None:
                break
            for profile in [Pleb.inflate(row[0]) for row in res]:
                if profile.last_counted_vote_node is not None:
                    continue
                else:
                    query = 'MATCH (v:Vote)<-[:LAST_VOTES]-' \
                            '(content:VotableContent)-[:OWNED_BY]->' \
                            '(p:Pleb {username: "%s"}) ' \
                            'WITH v ORDER BY v.created DESC ' \
                            'RETURN v LIMIT 1' % profile.username
                    res, _ = db.cypher_query(query)
                    res = res[0] if res else None
                    if res is not None:
                        profile.last_counted_vote_node = res['object_uuid']
                        profile.save()

        self.stdout.write("completed vote population\n", ending='')

        return True

    def handle(self, *args, **options):
        self.populate_last_reputation_node()
