from django.core.management.base import BaseCommand
from django.core.cache import cache

from neomodel import db

from sagebrew.sb_quests.neo_models import Quest


class Command(BaseCommand):
    args = 'None.'

    def set_quest_titles(self):
        query = 'MATCH (a:Quest) WHERE a.title IS NULL RETURN a'
        res, _ = db.cypher_query(query)
        for quest in [Quest.inflate(row[0]) for row in res]:
            quest.title = "%s %s" % (quest.first_name, quest.last_name)
            quest.save()
            cache.delete("%s_quest" % quest.object_uuid)
        self.stdout.write("completed quest titles\n", ending='')

    def handle(self, *args, **options):
        self.set_quest_titles()
