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
    cache_key = "recreated_official_quests"

    def remove_duplicate_quests(self):
        skip = 0
        while True:
            query = 'MATCH (official:PublicOfficial) ' \
                    'RETURN DISTINCT official ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res[0] if res else None:
                break
            for official in [PublicOfficial.inflate(row[0]) for row in res]:
                query = 'MATCH (official:PublicOfficial {object_uuid:"%s"})-' \
                        '[:IS_HOLDING]->(a:Quest) ' \
                        'OPTIONAL MATCH (a)-[r]-() ' \
                        'DELETE a, r' % official.object_uuid
                db.cypher_query(query)
                quest = Quest(
                    about=official.bio, youtube=official.youtube,
                    twitter=official.twitter, website=official.website,
                    first_name=official.first_name,
                    last_name=official.last_name,
                    owner_username=official.object_uuid,
                    title="%s %s" % (official.first_name, official.last_name),
                    profile_pic="%s/representative_images/225x275/"
                                "%s.jpg" %
                                (settings.LONG_TERM_STATIC_DOMAIN,
                                 official.bioguideid)).save()
                official.quest.connect(quest)
        cache.set(self.cache_key, True)

    def handle(self, *args, **options):
        if not cache.get(self.cache_key):
            self.remove_duplicate_quests()
        logger.info("Completed elasticsearch repopulation")
