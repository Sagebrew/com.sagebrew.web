from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from sb_public_official.neo_models import PublicOfficial
from sb_public_official.serializers import PublicOfficialSerializer


class Command(BaseCommand):
    args = 'None.'

    def update_official_search(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        for official in PublicOfficial.nodes.all():
            try:
                es.delete(index='full-search-base', doc_type='public_official',
                          id=official.object_uuid)
            except NotFoundError:
                pass
            es.index(index='full-search-base', doc_type='campaign',
                     id=official.object_uuid,
                     body=PublicOfficialSerializer(official).data)

    def handle(self, *args, **options):
        self.update_official_search()
