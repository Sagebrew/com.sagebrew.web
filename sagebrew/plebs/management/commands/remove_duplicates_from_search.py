from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch, NotFoundError


class Command(BaseCommand):
    args = 'None.'
    help = 'Remove duplicate Tyler in Search'

    def remove_duplicate(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            es.delete(index="full-search-base", id="devon_bleibtrey",
                      doc_type="profile")
        except NotFoundError:
            pass
        try:
            es.delete(index="full-search-base", id="devon_bleibtrey1",
                      doc_type="profile")
        except NotFoundError:
            pass
        try:
            es.delete(index="full-search-base", id="kate_wilson",
                      doc_type="profile")
        except NotFoundError:
            pass

    def handle(self, *args, **options):
        self.remove_duplicate()
