import logging
from json import dumps
from django.conf import settings
from elasticsearch import Elasticsearch
from neomodel.exception import UniqueProperty, DoesNotExist, CypherException

from .neo_models import SBAutoTag, SBTag
from sb_questions.neo_models import SBQuestion
from sb_base.utils import defensive_exception

logger = logging.getLogger('loggly_logs')


def create_tag_relations_util(tags):
    '''
    This function creates and manages the relationships between tags, such as
    the frequently_tagged_with relationship.

    :param tags:
    :return:
    '''
    if not tags:
        return False

    try:
        for tag in tags:
            temp_list = tags
            temp_list.remove(tag)
            for item in temp_list:
                if tag.frequently_auto_tagged_with.is_connected(item):
                    rel = tag.frequently_auto_tagged_with.relationship(item)
                    rel.count += 1
                    rel.save()
                else:
                    rel = tag.frequently_auto_tagged_with.connect(item)
                    rel.save()
        return True

    except Exception as e:
        return defensive_exception(create_tag_relations_util, e, e)


