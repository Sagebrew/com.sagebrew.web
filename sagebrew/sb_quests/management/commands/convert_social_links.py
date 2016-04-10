from django.core.management.base import BaseCommand

from neomodel import db

from sb_quests.neo_models import Quest


class Command(BaseCommand):
    args = 'None.'

    def convert_social_links(self):
        twitter_string = "https://www.twitter.com/%s"
        facebook_string = "https://www.facebook.com/%s"
        linkedin_string = "https://www.linkedin.com/in/%s"
        youtube_string = "https://www.youtube.com/user/%s"
        query = 'MATCH (q:Quest) RETURN q'
        res, _ = db.cypher_query(query)
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

    def handle(self, *args, **options):
        self.convert_social_links()
