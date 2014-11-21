from celery import shared_task

from api.utils import spawn_task
from .utils import add_auto_tags_util, add_tag_util, create_tag_relations_util



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
    response = add_tag_util(object_type, object_uuid, tags)
    if isinstance(response, Exception) is True:
        raise add_auto_tags.retry(exc=response, countdown=3,
                                  max_retries=None)
    else:
        return response


@shared_task()
def create_tag_relations(tag_array):
    response = create_tag_relations_util(tag_array)
    if isinstance(response, Exception) is True:
        raise create_tag_relations.retry(exc=response, countdown=3,
                                         max_retries=None)
    else:
        return response


@shared_task()
def add_auto_tags(tag_list):
    '''
    This function creates the auto generated tag nodes and connects them to the
    post from which they were tagged.

    :param tag_list:
    :return:
    '''
    response_list = []
    if len(tag_list) < 1:
        return True

    response = add_auto_tags_util(tag_list)

    if isinstance(response, Exception) is True:
        raise add_auto_tags.retry(exc=response, countdown=3,
                                  max_retries=None)
    else:
        spawn_task(task_func=create_tag_relations,
                   task_param={"tag_array": tag_list})
        return response