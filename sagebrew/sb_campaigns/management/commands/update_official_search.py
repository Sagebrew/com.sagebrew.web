from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, TransportError

from sb_public_official.neo_models import PublicOfficial

from sb_campaigns.neo_models import PoliticalCampaign
from sb_campaigns.serializers import PoliticalCampaignSerializer


class Command(BaseCommand):
    args = 'None.'

    def update_official_search(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        for official in PublicOfficial.nodes.all():
            camp = PoliticalCampaign.nodes.get(
                object_uuid=official.get_campaign().object_uuid)
            try:
                es.delete(index='full-search-base', doc_type='public_official',
                          id=official.object_uuid)
            except (NotFoundError, TransportError):
                pass
            data = PoliticalCampaignSerializer(camp).data
            es.index(index='full-search-base', doc_type='campaign',
                     id=camp.object_uuid,
                     body=data)

    def handle(self, *args, **options):
        self.update_official_search()
