from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch

class Command(BaseCommand):
    args = 'None.'
    help = 'Flushes all info in every elasticsearch index. DO NOT USE ' \
           'OUTSIDE OF DEV ENVIRONMENT.'

    def empty_elasticsearch(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.indices.delete(index='_all', ignore=[400, 404])
        es.indices.create(index='tags')
        es.indices.create(index='full-search-base')
        es.indices.create(index='full-search-user-specific-1')
        print "Flushed all data"

    def handle(self, *args, **options):
        self.empty_elasticsearch()