from logging import getLogger
from celery import shared_task

from api.utils import spawn_task

from sb_base.neo_models import TaggableContent
from .neo_models import AutoTag
from .utils import create_tag_relations_util, update_tags_util

logger = getLogger("loggly_logs")


@shared_task()
def create_tag_relations(tag_array):
    response = create_tag_relations_util(
        [AutoTag.nodes.get(object_uuid=object_uuid)
         for object_uuid in tag_array])
    if isinstance(response, Exception) is True:  # pragma: no cover
        # Not covering as we don't have a consistent way of reproducing it
        # currently. - Devon Bleibtrey
        raise create_tag_relations.retry(exc=response, countdown=3,
                                         max_retries=None)
    else:
        return response


@shared_task()
def add_auto_tags(object_uuid, tag_list):
    """
    This function creates the auto generated tag nodes and connects them to the
    post from which they were tagged.

    :param object_uuid
    :param tag_list:
    :return:
    """
    if len(tag_list) < 1:
        return True
    content = TaggableContent.nodes.get(object_uuid=object_uuid)
    response = content.add_auto_tags(tag_list)

    if isinstance(response, Exception) is True:  # pragma: no cover
        # Not covering as we don't have a consistent way of reproducing it
        # currently. - Devon Bleibtrey
        raise add_auto_tags.retry(exc=response, countdown=3,
                                  max_retries=None)

    spawned = spawn_task(
        task_func=create_tag_relations,
        task_param={"tag_array": [tag.object_uuid for tag in response]})
    if isinstance(spawned, Exception) is True:  # pragma: no cover
        # Not covering as we don't have a consistent way of reproducing it
        # currently. - Devon Bleibtrey
        raise add_auto_tags.retry(exc=response, countdown=3,
                                  max_retries=None)
    return response


@shared_task()
def update_tags(tags):
    """
    Takes a list of tag names that have been utilized on some piece of content
    and performs the necessary updates. Such as incrementing tag_used by 1
    and associating the tags with each other as frequently_tagged_with.

    :param tags: List of strings representing tag names
    :return:
    """
    updates = update_tags_util(tags)
    if isinstance(updates, Exception):  # pragma: no cover
        # Not covering as we don't have a consistent way of reproducing it
        # currently. - Devon Bleibtrey
        raise update_tags.retry(exc=updates, countdown=3, max_retries=None)

    return updates
