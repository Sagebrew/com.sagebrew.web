from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch

from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_campaigns.neo_models import PoliticalCampaign
from sb_campaigns.serializers import PoliticalCampaignSerializer


class Command(BaseCommand):
    args = 'None.'

    def repopulate_elasticsearch(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        for question in Question.nodes.all():
            es.index(index='full-search-base', doc_type='question',
                     id=question.object_uuid,
                     body=QuestionSerializerNeo(question).data)
        for pleb in Pleb.nodes.all():
            es.index(index='full-search-base', doc_type='profile',
                     id=pleb.username, body=PlebSerializerNeo(pleb).data)
        for campaign in PoliticalCampaign.nodes.all():
            es.index(index='full-search-base', doc_type='campaign',
                     id=campaign.object_uuid,
                     body=PoliticalCampaignSerializer(campaign).data)

    def handle(self, *args, **options):
        self.repopulate_elasticsearch()
