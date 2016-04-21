from logging import getLogger

from django.core.cache import cache
from django.core.management.base import BaseCommand

from neomodel import db

from sb_quests.neo_models import Quest

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'
    cache_key = "removed_duplicate_quests"

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
                        '(q)-[:EDITOR_OF|MODERATOR_OF|FOLLOWERS|IS_WAGING]-' \
                        '(:Pleb) AND NOT (q)<-[:IS_HOLDING]-' \
                        '(:PublicOfficial) AND NOT (q)-[:EMBARKS_ON]->' \
                        '(:Mission) WITH q ' \
                        'OPTIONAL MATCH (q)-[r]-() ' \
                        'DELETE q, r' % (quest.object_uuid)
                res, _ = db.cypher_query(query)
        cache.set("removed_duplicate_quests", True)

    def handle(self, *args, **options):
        self.remove_duplicate_quests()
        logger.info("Completed elasticsearch repopulation")
