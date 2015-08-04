from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from sb_public_official.neo_models import PublicOfficial

from sb_campaigns.neo_models import PoliticalCampaign


class Command(BaseCommand):
    args = 'None.'

    def remove_official_search(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        for official in PublicOfficial.nodes.all():
            try:
                es.delete(index='full-search-base', doc_type='public_official',
                          id=official.object_uuid)
            except (NotFoundError):
                try:
                    es.delete(index='full-search-base',
                              doc_type='politicalcampaign',
                              id=official.object_uuid)
                except (NotFoundError):
                    try:
                        es.delete(index='full-search-base',
                                  doc_type='campaign',
                                  id=official.object_uuid)
                    except (NotFoundError):
                        pass
        for camp in PoliticalCampaign.nodes.all():
            try:
                es.delete(index='full-search-base', doc_type='public_official',
                          id=camp.object_uuid)
            except (NotFoundError):
                try:
                    es.delete(index='full-search-base',
                              doc_type='politicalcampaign',
                              id=camp.object_uuid)
                except (NotFoundError):
                    try:
                        es.delete(index='full-search-base',
                                  doc_type='campaign',
                                  id=camp.object_uuid)
                    except (NotFoundError):
                        pass

    def handle(self, *args, **options):
        self.remove_official_search()
