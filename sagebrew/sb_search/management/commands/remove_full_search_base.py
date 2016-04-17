from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch


class Command(BaseCommand):
    args = 'None.'
    help = 'Deletes and recreates full-search-base Elasticsearch index'

    def empty_elasticsearch(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.indices.delete(index='full-search-base', ignore=[400, 404])
        es.indices.create(index='full-search-base')
        print("Flushed full-search-base data")

    def handle(self, *args, **options):
        self.empty_elasticsearch()
