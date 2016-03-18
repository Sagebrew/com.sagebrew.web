from django.core.management.base import BaseCommand

from sb_quests.neo_models import Quest


class Command(BaseCommand):
    args = 'None.'

    def set_quest_titles(self):
        for quest in Quest.nodes.all():
            if not quest.title:
                quest.title = "%s %s" % (quest.first_name, quest.last_name)
                quest.save()

    def handle(self, *args, **options):
        self.set_quest_titles()
