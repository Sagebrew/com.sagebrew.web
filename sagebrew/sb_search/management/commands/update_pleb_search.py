from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.cache import cache

from elasticsearch import Elasticsearch

from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo


class Command(BaseCommand):
    args = 'None.'

    def update_pleb_search(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        pleb = Pleb.nodes.get(username="chris_cunningham")
        res = es.index(index='full-search-base', doc_type='profile',
                       id=pleb.object_uuid, body=PlebSerializerNeo(pleb).data)
        pleb.search_id = res['_id']
        pleb.populated_es_index = True
        pleb.save()
        cache.delete("%s_vote_search_update" % pleb.object_uuid)
        cache.delete(pleb.username)

    def handle(self, *args, **options):
        self.update_pleb_search()
