from celery import shared_task

from api.utils import spawn_task

from .utils import create_tag_relations_util, calc_spheres, update_tags_util


@shared_task()
def add_tags(question, tags):
    '''
    This calls the util to add user generated tags to the object. It creates
    the tags in the neo4j DB if they don't exist and if they do, it gets
    them then creates the relationship between them.

    :param object_uuid:
    :param tags:
    :return:
    '''
    response = question.add_tags(tags)
    if isinstance(response, Exception) is True:
        raise add_tags.retry(exc=response, countdown=3, max_retries=None)
    spawned = spawn_task(create_tag_relations, {"tag_array": response})
    if isinstance(spawned, Exception) is True:
        raise add_tags.retry(exc=response, countdown=3, max_retries=None)

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
def add_auto_tags(question, tag_list):
    '''
    This function creates the auto generated tag nodes and connects them to the
    post from which they were tagged.

    :param tag_list:
    :return:
    '''
    if len(tag_list) < 1:
        return True
    response = question.add_auto_tags(tag_list)

    if isinstance(response, Exception) is True:
        raise add_auto_tags.retry(exc=response, countdown=3,
                                  max_retries=None)

    spawned = spawn_task(task_func=create_tag_relations,
                         task_param={"tag_array": response})
    if isinstance(spawned, Exception) is True:
        raise add_auto_tags.retry(exc=response, countdown=3,
                                  max_retries=None)
    return response


@shared_task()
def calc_spheres_task():
    res = calc_spheres()
    if isinstance(res, Exception):
        raise calc_spheres.retry(exc=res, countdown=3, max_retries=None)
    return res


@shared_task()
def update_tags(tags):
    '''
    Takes a list of tag names that have been utilized on some piece of content
    and performs the necessary updates. Such as incrementing tag_used by 1
    and associating the tags with each other as frequently_tagged_with.

    :param tags: List of strings representing tag names
    :return:
    '''
    updates = update_tags_util(tags)
    if isinstance(updates, Exception):
        raise update_tags.retry(exc=updates, countdown=3, max_retries=None)

    return updates