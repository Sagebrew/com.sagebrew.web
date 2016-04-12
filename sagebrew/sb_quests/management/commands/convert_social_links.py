from logging import getLogger

from django.core.cache import cache
from django.core.management.base import BaseCommand

from neomodel import db, CypherException

from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission
logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'

    def convert_social_links(self):
        twitter_string = "https://www.twitter.com/"
        facebook_string = "https://www.facebook.com/"
        linkedin_string = "https://www.linkedin.com/in/"
        youtube_string = "https://www.youtube.com/user/"
        skip = 0
        while True:
            query = 'MATCH (q:Quest) RETURN q ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            try:
                for quest in [Quest.inflate(row[0]) for row in res]:
                    if quest.twitter and twitter_string not in quest.twitter:
                        quest.twitter = "%s%s" % (twitter_string, quest.twitter)
                    if quest.facebook and facebook_string not in quest.facebook:
                        quest.facebook = "%s%s" % (
                            facebook_string, quest.facebook)
                    if quest.linkedin and linkedin_string not in quest.linkedin:
                        quest.linkedin = "%s%s" % (
                            linkedin_string, quest.linkedin)
                    if quest.youtube and youtube_string not in quest.youtube:
                        quest.youtube = "%s%s" % (youtube_string, quest.youtube)
                    quest.save()
                    cache.delete("%s_quest" % quest.object_uuid)
            except (CypherException, Exception):
                logger.exception("Convert Social Links: ")
                pass
        try:
            res, _ = db.cypher_query('MATCH (a:Mission) RETURN a')
            for mission in [Mission.inflate(row[0]) for row in res]:
                if mission.twitter and twitter_string not in mission.twitter:
                    mission.twitter = "%s%s" % (twitter_string, mission.twitter)
                if mission.facebook and facebook_string not in mission.facebook:
                    mission.facebook = "%s%s" % (
                        facebook_string, mission.facebook)
                if mission.linkedin and linkedin_string not in mission.linkedin:
                    mission.linkedin = "%s%s" % (
                        linkedin_string, mission.linkedin)
                if mission.youtube and youtube_string not in mission.youtube:
                    mission.youtube = "%s%s" % (youtube_string, mission.youtube)
                mission.save()
                cache.delete("%s_mission" % mission.object_uuid)
        except (CypherException, Exception):
            logger.exception("Convert Social Links: ")
            pass

    def handle(self, *args, **options):
        self.convert_social_links()
