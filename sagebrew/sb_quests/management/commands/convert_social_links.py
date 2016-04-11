from logging import getLogger
from django.core.management.base import BaseCommand

from neomodel import db, CypherException

from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission
logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'

    def convert_social_links(self):
        twitter_string = "https://www.twitter.com/%s"
        facebook_string = "https://www.facebook.com/%s"
        linkedin_string = "https://www.linkedin.com/in/%s"
        youtube_string = "https://www.youtube.com/user/%s"
        try:
            res, _ = db.cypher_query('MATCH (q:Quest) RETURN q')
            for quest in [Quest.inflate(row[0]) for row in res]:
                if quest.twitter:
                    quest.twitter = twitter_string % quest.twitter
                if quest.facebook:
                    quest.facebook = facebook_string % quest.facebook
                if quest.linkedin:
                    quest.linkedin = linkedin_string % quest.linkedin
                if quest.youtube:
                    quest.youtube = youtube_string % quest.youtube
                quest.save()
        except (CypherException, Exception) as e:
            logger.exception("Convert Social Links: ")
            pass
        try:
            res, _ = db.cypher_query('MATCH (a:Mission) RETURN a')
            for mission in [Mission.inflate(row[0]) for row in res]:
                if mission.twitter:
                    mission.twitter = twitter_string % mission.twitter
                if mission.facebook:
                    mission.facebook = facebook_string % mission.facebook
                if mission.linkedin:
                    mission.linkedin = linkedin_string % mission.linkedin
                if mission.youtube:
                    mission.youtube = youtube_string % mission.youtube
                mission.save()
        except (CypherException, Exception) as e:
            logger.exception("Convert Social Links: ")
            pass

    def handle(self, *args, **options):
        self.convert_social_links()
