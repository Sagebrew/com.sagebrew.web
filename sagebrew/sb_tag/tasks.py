from celery import shared_task

from .utils import add_auto_tags_util

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

    if len(tag_list) <= 1:
        return True

    response = (add_auto_tags_util(tag_list))

    if response:
        return True
    else:
        return False
