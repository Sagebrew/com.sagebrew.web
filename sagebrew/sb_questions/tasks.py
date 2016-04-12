from logging import getLogger

from celery import shared_task

from django.core.cache import cache

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task, create_auto_tags, generate_summary
from sb_tags.tasks import add_auto_tags

from .neo_models import Question

logger = getLogger("loggly_logs")


@shared_task()
def create_question_summary_task(object_uuid):
    try:
        question = Question.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Question.DoesNotExist, CypherException, IOError) as e:
        raise create_question_summary_task.retry(exc=e, countdown=5,
                                                 max_retries=None)
    summary = generate_summary(question.content)
    if summary is not None and summary != "":
        question.summary = summary
    question.save()
    cache.delete(question.object_uuid)

    return question


@shared_task()
def add_auto_tags_to_question_task(object_uuid):
    """
    This function will take a question object, a list of
    tags and auto tags and manage the other tasks which attach them to
    the question.

    :param object_uuid:
    :return:
    """
    try:
        question = Question.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Question.DoesNotExist, CypherException, IOError) as e:
        raise add_auto_tags_to_question_task.retry(exc=e, countdown=5,
                                                   max_retries=None)
    auto_tags = create_auto_tags(question.content)
    if isinstance(auto_tags, Exception) is True:  # pragma: no cover
        # Not covering because we don't have a good way to generate this
        # exception - Devon Bleibtrey
        raise add_auto_tags_to_question_task.retry(
            exc=auto_tags, countdown=3, max_retries=None)

    task_data = []
    for tag in auto_tags.get('keywords', []):
        task_data.append({"tags": tag})

    auto_tag_data = {
        'object_uuid': question.object_uuid,
        'tag_list': task_data
    }
    spawned = spawn_task(task_func=add_auto_tags,
                         task_param=auto_tag_data)
    if isinstance(spawned, Exception) is True:  # pragma: no cover
        # Not covering because we don't have a good way to generate this
        # exception - Devon Bleibtrey
        raise add_auto_tags_to_question_task.retry(exc=spawned, countdown=3,
                                                   max_retries=None)

    return spawned
