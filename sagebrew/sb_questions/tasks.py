from celery import shared_task

from django.conf import settings

from neomodel import CypherException, DoesNotExist

from elasticsearch import Elasticsearch

from api.utils import spawn_task, create_auto_tags
from api.tasks import add_object_to_search_index
from sb_tags.tasks import add_auto_tags

from .neo_models import Question


@shared_task()
def add_question_to_indices_task(question):
    '''
    This function will take a question object and a string of tags which
    the user has tagged the question as. It will then add the question
    data to the elasticsearch base index.

    :param question:
    :param tags:
    :return:
    '''
    try:
        question_obj = Question.nodes.get(object_uuid=question["object_uuid"])
        if question_obj.added_to_search_index is True:
            return True
    except (CypherException, IOError) as e:
        raise add_question_to_indices_task.retry(exc=e, countdown=3,
                                                 max_retries=None)

    task_data = {
        "object_uuid": question['object_uuid'],
        'object_data': question
    }
    spawned = spawn_task(task_func=add_object_to_search_index,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise add_question_to_indices_task.retry(exc=spawned, countdown=3,
                                                 max_retries=None)
    try:
        question_obj.added_to_search_index = True
        question_obj.save()
    except (CypherException, IndexError) as e:
        raise add_question_to_indices_task.retry(exc=e, countdown=3,
                                                 max_retries=None)

    return True


@shared_task()
def add_auto_tags_to_question_task(object_uuid):
    '''
    This function will take a question object, a list of
    tags and auto tags and manage the other tasks which attach them to
    the question.

    :param question:
    :return:
    '''
    try:
        question = Question.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Question.DoesNotExist, CypherException, IOError) as e:
        raise add_auto_tags_to_question_task.retry(exc=e, countdown=5,
                                                   max_retries=None)
    auto_tags = create_auto_tags(question.content)
    if isinstance(auto_tags, Exception) is True:
        raise add_auto_tags_to_question_task.retry(
            exc=auto_tags, countdown=3, max_retries=None)

    task_data = []
    for tag in auto_tags.get('keywords', []):
        task_data.append({"tags": tag})

    auto_tag_data = {
        'question': question,
        'tag_list': task_data
    }
    spawned = spawn_task(task_func=add_auto_tags,
                         task_param=auto_tag_data)
    if isinstance(spawned, Exception) is True:
        raise add_auto_tags_to_question_task.retry(exc=spawned, countdown=3,
                                                   max_retries=None)

    return spawned


@shared_task()
def update_search_index(object_uuid):
    from .serializers import QuestionSerializerNeo
    try:
        question = Question.nodes.get(object_uuid=object_uuid)
    except (CypherException, IOError) as e:
        raise add_auto_tags_to_question_task.retry(exc=e, countdown=3,
                                                   max_retries=None)
    document = QuestionSerializerNeo(question).data
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    es.update(index="full-search-base",
              doc_type=document['type'],
              id=document['id'], body=document)

    return True
