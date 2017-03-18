from json import loads, dumps
from logging import getLogger
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify

from elasticsearch import Elasticsearch
from neo4j.v1 import CypherError
from neomodel import DoesNotExist

from sagebrew.sb_tags.neo_models import Tag

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'

    def populate_base_tags(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        with open('%s/sb_tags/management/commands'
                  '/initial_tags.json' % settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            for tag in data['tags']:
                try:
                    tag_node = Tag.nodes.get(name=slugify(tag['name']))
                except (Tag.DoesNotExist, DoesNotExist):
                    tag_node = Tag(name=slugify(tag['name']), base=True).save()
                except (CypherError, IOError):
                    logger.exception(
                        dumps(
                            {"detail": "Cypher exception, "
                                       "failed to create "
                                       "tag %s" % tag['name']}))
                    continue
                es.index(index="tags", doc_type="tag",
                         body={"name": tag['name']})
                for sub_tag in tag['sub_tags']:
                    try:
                        sub_tag_node = Tag.nodes.get(name=slugify(sub_tag))
                    except (Tag.DoesNotExist, DoesNotExist):
                        sub_tag_node = Tag(name=slugify(sub_tag),
                                           base=False).save()
                    except (CypherError, IOError):
                        logger.exception(
                            dumps(
                                {"detail": "Cypher exception, "
                                           "failed to create tag "
                                           "%s" % tag['name']}))
                        continue
                    es.index(index='tags', doc_type='tag',
                             body={"name": sub_tag})
                    try:
                        rel = tag_node.frequently_tagged_with.connect(
                            sub_tag_node)
                        rel.in_sphere = True
                        rel.save()
                        rel = sub_tag_node.frequently_tagged_with.connect(
                            tag_node)
                        rel.in_sphere = True
                        rel.save()
                    except (CypherError, IOError):
                        logger.exception(
                            dumps(
                                {
                                    "detail":
                                        "Cypher exception, failed to create "
                                        "tag %s" % tag['name']
                                }))
                        continue

    def handle(self, *args, **options):
        self.populate_base_tags()
