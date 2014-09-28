import logging
from celery import shared_task

from .utils import add_auto_tags_util, add_tag_util

logger = logging.getLogger('loggly_logs')

@shared_task()
def add_auto_tags(tag_list):
    '''
    This function creates the auto generated tag nodes and connects them to the
    post from which they were tagged.

    :param tag:
    :param object_uuid:
    :param object_type:
    :return:
    '''
    response_list = []
    if len(tag_list) < 1:
        return True

    response = add_auto_tags_util(tag_list)

    if response:
        return True
    elif response is None:
        raise Exception
    else:
        return False


@shared_task()
def add_tags(object_uuid, object_type, tags):
    '''
    This calls the util to add user generated tags to the object. It creates
    the tags in the neo4j DB if they don't exist and if they do, it gets
    them then creates the relationship between them.

    :param object_uuid:
    :param object_type:
    :param tags:
    :return:
    '''
    if add_tag_util(object_type, object_uuid, tags):
        return True
    else:
        return False
