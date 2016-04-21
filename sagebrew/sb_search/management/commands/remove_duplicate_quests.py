from logging import getLogger

from django.core.management.base import BaseCommand

from neomodel import db

from sb_quests.neo_models import Quest

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'

    def remove_duplicate_quests(self):
        skip = 0
        while True:
            query = 'MATCH (quest:Quest) RETURN DISTINCT quest ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for quest in [Quest.inflate(row[0]) for row in res]:
                new_query = 'MATCH (a:Quest {owner_username: "%s"}) ' \
                            'RETURN a' % quest.owner_username
                new_res, _ = db.cypher_query(new_query)
                duplicate_quests = [Quest.inflate(duplicate[0])
                                    for duplicate in new_res
                                    if duplicate[0] is not None]
                if len(duplicate_quests) > 1:
                    skip = 0
                    duplicate_quests = duplicate_quests[1:]
                    for dup in duplicate_quests:
                        query = 'MATCH (a:Quest {object_uuid: "%s"}) ' \
                                'OPTIONAL MATCH (a)-[r]-() ' \
                                'DELETE a, r' % dup.object_uuid
                        db.cypher_query(query)

    def handle(self, *args, **options):
        self.remove_duplicate_quests()
        logger.info("Completed elasticsearch repopulation")
