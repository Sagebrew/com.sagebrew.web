from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch, NotFoundError

from api.utils import spawn_task
from sb_search.tasks import update_search_object
from plebs.neo_models import Pleb


class Command(BaseCommand):
    args = 'None.'
    help = 'Remove duplicate Tyler in Search'

    def remove_duplicate(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            es.delete(index="full-search-base", id="devon_bleibtrey",
                      doc_type="quest")
        except NotFoundError:
            pass
        for pleb in Pleb.nodes.all():
            es.delete(index="full-search-base", id=pleb.username,
                      doc_type="profile")

    def handle(self, *args, **options):
        self.remove_duplicate()
