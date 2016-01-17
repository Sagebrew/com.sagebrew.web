from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch

from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo


class Command(BaseCommand):
    args = 'None.'

    def update_pleb_search(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        for pleb in Pleb.nodes.all():
            es.index(index='full-search-base', doc_type='profile',
                     id=pleb.object_uuid, body=PlebSerializerNeo(pleb).data)

    def handle(self, *args, **options):
        self.update_pleb_search()
