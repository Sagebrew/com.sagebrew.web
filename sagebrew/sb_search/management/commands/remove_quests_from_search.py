from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch

from sb_quests.neo_models import Quest


class Command(BaseCommand):
    args = 'None.'
    help = 'Removes all quests from search'

    def remove_quests_from_search(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        for quest in Quest.nodes.all():
            es.delete(index='full-search-base', ignore=[400, 404],
                      doc_type='quest', id=quest.object_uuid)
        print("Removed all quests from full-search-base")

    def handle(self, *args, **options):
        self.remove_quests_from_search()
