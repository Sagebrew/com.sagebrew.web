from json import loads, dumps
from logging import getLogger
from django.core.management.base import BaseCommand
from django.conf import settings

from neomodel import DoesNotExist, CypherException

from sb_tag.neo_models import SBTag

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'

    def populate_base_tags(self):
        with open('%s/api/management/commands'
                  '/initial_tags.json' % settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            for tag in data['tags']:
                try:
                    tag_node = SBTag.nodes.get(tag_name=tag['tag_name'])
                except (SBTag.DoesNotExist, DoesNotExist):
                    tag_node = SBTag(tag_name=tag['tag_name'], base=True).save()
                except (CypherException, IOError):
                    logger.exception(
                        dumps(
                            {"detail": "Cypher exception, failed to create tag %s"
                                       % tag['tag_name']}))
                    continue
                for sub_tag in tag['sub_tags']:
                    try:
                        sub_tag = SBTag.nodes.get(tag_name=sub_tag)
                    except (SBTag.DoesNotExist, DoesNotExist):
                        sub_tag = SBTag(tag_name=sub_tag, base=False).save()
                    except (CypherException, IOError):
                        logger.exception(
                            dumps(
                                {"detail": "Cypher exception, failed to create tag %s"
                                           % tag['tag_name']}))
                        continue
                    try:
                        rel = tag_node.frequently_tagged_with.connect(sub_tag)
                        rel.in_sphere = True
                        rel.save()
                        rel = sub_tag.frequently_tagged_with.connect(tag_node)
                        rel.in_sphere = True
                        rel.save()
                    except (CypherException, IOError):
                        logger.exception(
                            dumps(
                                {"detail": "Cypher exception, failed to create tag %s"
                                           % tag['tag_name']}))
                        continue

    def handle(self, *args, **options):
        self.populate_base_tags()