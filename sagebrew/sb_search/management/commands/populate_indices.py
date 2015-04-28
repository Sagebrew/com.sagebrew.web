from logging import getLogger

from django.core.management.base import BaseCommand
from django.conf import settings

from elasticsearch import Elasticsearch

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'

    def populate_indices(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        if not es.indices.exists('full-search-base'):
            es.indices.create('full-search-base')
        if not es.indices.exists('tags'):
            es.indices.create('tags')
        if not es.indices.exists('full-search-user-specific-1'):
            es.indices.create('full-search-user-specific-1')

    def handle(self, *args, **options):
        self.populate_indices()
        logger.info("Completed index population")
