from logging import getLogger

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand

from neomodel import db

from sagebrew.sb_quests.neo_models import Quest
from sagebrew.sb_public_official.neo_models import PublicOfficial

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'
    cache_key = "removed_duplicate_quests"

    def remove_duplicate_quests(self):
        skip = 0
        while True:
            query = 'MATCH (official:PublicOfficial) ' \
                    'RETURN DISTINCT official ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for official in [PublicOfficial.inflate(row[0]) for row in res]:
                new_query = 'MATCH (a:Quest {owner_username: "%s"}) ' \
                            'RETURN a' % official.object_uuid
                new_res, _ = db.cypher_query(new_query)
                if not new_res.one:
                    quest = Quest(
                        about=official.bio, youtube=official.youtube,
                        twitter=official.twitter, website=official.website,
                        first_name=official.first_name,
                        last_name=official.last_name,
                        owner_username=official.object_uuid,
                        title="%s %s" % (
                            official.first_name, official.last_name),
                        profile_pic="%s/representative_images/225x275/"
                                    "%s.jpg" %
                                    (settings.LONG_TERM_STATIC_DOMAIN,
                                     official.bioguideid)).save()
                    official.quest.connect(quest)
                duplicate_query = 'MATCH (a:PublicOfficial ' \
                                  '{object_uuid:"%s"})-' \
                                  '[:IS_HOLDING]->(q:Quest) ' \
                                  'WHERE NOT q.owner_username="%s" RETURN q' % \
                                  (official.object_uuid, official.object_uuid)
                new_res, _ = db.cypher_query(duplicate_query)
                duplicate_quests = [Quest.inflate(duplicate[0])
                                    for duplicate in new_res
                                    if duplicate[0] is not None]
                if duplicate_quests:
                    skip = 0
                    for dup in duplicate_quests:
                        relationship_query = 'MATCH (a:Quest ' \
                                             '{object_uuid:"%s"})-[r]-' \
                                             '(p:Pleb) RETURN ' \
                                             'p.username as username, ' \
                                             'type(r) as type' \
                                             % dup.object_uuid
                        rel_res, _ = db.cypher_query(relationship_query)
                        if rel_res.one:
                            for row in rel_res:
                                try:
                                    re_query = 'MATCH (a:Quest ' \
                                               '{owner_username:"%s"}), ' \
                                               '(p:Pleb {username:"%s"}) ' \
                                               'CREATE UNIQUE (p)-[r:%s]->(a)' \
                                               % (official.object_uuid,
                                                  row.username, row.type)
                                    db.cypher_query(re_query)
                                except ConstraintViolation:
                                    # handle potential constraint violations
                                    pass
                        query = 'MATCH (a:Quest {object_uuid: "%s"}) ' \
                                'OPTIONAL MATCH (a)-[r]-() ' \
                                'DELETE a, r' % dup.object_uuid
                        db.cypher_query(query)
        cache.set("removed_duplicate_quests", True)

    def handle(self, *args, **options):
        if not cache.get(self.cache_key):
            self.remove_duplicate_quests()
        logger.info("Completed elasticsearch repopulation")
