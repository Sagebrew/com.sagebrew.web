from logging import getLogger

from django.core.cache import cache
from django.core.management.base import BaseCommand

from neomodel import db

from sagebrew.sb_quests.neo_models import Quest

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'
    cache_key = "removed_unconnected_quests"

    def remove_duplicate_quests(self):
        skip = 0
        while True:
            query = 'MATCH (q:Quest) ' \
                    'RETURN DISTINCT q ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for quest in [Quest.inflate(row[0]) for row in res]:
                query = 'MATCH (q:Quest {object_uuid:"%s"}) WHERE NOT ' \
                        '(q)-[]-(:Pleb) AND NOT (q)-[]-(:PublicOfficial) ' \
                        'AND NOT (q)-[]-(:Mission) WITH q ' \
                        'OPTIONAL MATCH (q)-[r]-() ' \
                        'DELETE q, r' % quest.object_uuid
                res, _ = db.cypher_query(query)
        cache.set(self.cache_key, True)

    def handle(self, *args, **options):
        if not cache.get(self.cache_key):
            self.remove_duplicate_quests()
        logger.info("Completed elasticsearch repopulation")
