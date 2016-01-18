from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from plebs.neo_models import Pleb


class Command(BaseCommand):
    args = 'None.'

    def update_pleb_search(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        for pleb in Pleb.nodes.all():
            try:
                es.delete(index='full-search-base', doc_type='profile',
                          id=pleb.username)
            except NotFoundError:
                pass

    def handle(self, *args, **options):
        self.update_pleb_search()
