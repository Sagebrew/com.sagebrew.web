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
        try:
            es.delete(index="full-search-base", id="devon_bleibtrey",
                      doc_type="campaign")
        except NotFoundError:
            pass
        try:
            es.delete(index="full-search-base", id="devon_bleibtrey",
                      doc_type="politicalcampaign")
        except NotFoundError:
            pass
        try:
            es.delete(index="full-search-base", id="kate_wilson",
                      doc_type="profile")
        except NotFoundError:
            pass
        try:
            es.delete(index="full-search-base", id="kate_wilson",
                      doc_type="quest")
        except NotFoundError:
            pass
        try:
            es.delete(index="full-search-base", id="kate_wilson",
                      doc_type="campaign")
        except NotFoundError:
            pass
        try:
            es.delete(index="full-search-base", id="kate_wilson",
                      doc_type="politicalcampaign")
        except NotFoundError:
            pass
        try:
            es.delete(index="full-search-base", id="keenan_gottschall",
                      doc_type="profile")
        except NotFoundError:
            pass
        pleb = Pleb.get(username="robin_branch", cache_buster=True)
        task_data = {
            "object_uuid": pleb.object_uuid,
            "label": 'pleb'
        }
        spawn_task(
            task_func=update_search_object,
            task_param=task_data,
            countdown=30)
        pleb = Pleb.get(username="rebecca_tanner", cache_buster=True)
        task_data = {
            "object_uuid": pleb.object_uuid,
            "label": 'pleb'
        }
        spawn_task(
            task_func=update_search_object,
            task_param=task_data,
            countdown=30)

    def handle(self, *args, **options):
        self.remove_duplicate()
