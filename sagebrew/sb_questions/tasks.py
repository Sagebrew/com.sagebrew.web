from django.conf import settings

from celery import shared_task
from neomodel import CypherException
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (ElasticsearchException, TransportError,
                                      ConnectionError, RequestError,
                                      NotFoundError)

from api.utils import spawn_task, create_auto_tags
from api.tasks import add_object_to_search_index
from sb_tag.tasks import add_auto_tags, add_tags
from sb_base.tasks import create_object_relations_task
from sb_docstore.tasks import build_question_page_task
from .utils import create_question_util


@shared_task()
def add_question_to_indices_task(question, tags):
    '''
    This function will take a question object and a string of tags which
    the user has tagged the question as. It will then add the question
    data to the elasticsearch base index.

    :param question:
    :param tags:
    :return:
    '''
    try:
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res = es.get(index='full-search-base',
                     doc_type='sb_questions.neo_models.SBQuestion',
                     id=question.sb_id)
        return True
    except NotFoundError:
        pass
    except (ElasticsearchException, TransportError, ConnectionError,
            RequestError) as e:
        raise add_question_to_indices_task.retry(exc=e, countdown=3,
                                                 max_retries=None)

    search_dict = {'question_content': question.content,
                   'user': question.owned_by.all()[0].email,
                   'question_title': question.question_title,
                   'tags': tags,
                   'object_uuid': question.sb_id,
                   'post_date': question.date_created,
                   'related_user': ''}
    task_data = {"object_type": "sb_questions.neo_models.SBQuestion",
                 "object_data": search_dict}
    question.added_to_search_index = True
    try:
        question.save()
    except (CypherException, IndexError) as e:
        raise add_question_to_indices_task.retry(exc=e, countdown=3,
                                                 max_retries=None)
    spawned = spawn_task(task_func=add_object_to_search_index,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise add_question_to_indices_task.retry(exc=spawned, countdown=3,
                                                 max_retries=None)
    return True




@shared_task()
def add_tags_to_question_task(question, tags):
    '''
    This function will take a question object, a list of
    tags and auto tags and manage the other tasks which attach them to
    the question.

    :param question:
    :param tags:
    :return:
    '''
    if question.tags_added is True:
        task_data = {
            'question': question,
            'tags': tags
        }
        spawned = spawn_task(task_func=add_question_to_indices_task,
                             task_param=task_data)
        if isinstance(spawned, Exception) is True:
            raise add_tags_to_question_task.retry(exc=spawned, countdown=3,
                                                  max_retries=None)
    else:
        auto_tags = create_auto_tags(question.content)
        if isinstance(auto_tags, Exception) is True:
            raise add_tags_to_question_task.retry(
                exc=auto_tags, countdown=3, max_retries=None)
        task_data = []
        try:
            for tag in auto_tags['keywords']:
                task_data.append({"tags": tag})
        except KeyError:
            pass
        auto_tag_data = {'question': question,
                         'tag_list': task_data}
        tag_task_data = {'question': question,
                         "tags": tags}
        spawned = spawn_task(task_func=add_tags, task_param=tag_task_data)
        if isinstance(spawned, Exception) is True:
            raise add_tags_to_question_task.retry(exc=spawned, countdown=3,
                                                  max_retries=None)
        spawned = spawn_task(task_func=add_auto_tags,
                             task_param=auto_tag_data)
        if isinstance(spawned, Exception) is True:
            raise add_tags_to_question_task.retry(exc=spawned, countdown=3,
                                                  max_retries=None)
        question.tags_added = True
        try:
            question.save()
        except CypherException as e:
            raise add_tags_to_question_task.retry(exc=e, countdown=3,
                                                  max_retries=None)
        spawned = spawn_task(task_func=add_question_to_indices_task,
                             task_param={'question': question,
                                         'tags': tags})
        if isinstance(spawned, Exception) is True:
            raise add_tags_to_question_task.retry(exc=spawned, countdown=3,
                                                  max_retries=None)
        return spawned


@shared_task()
def create_question_task(content, current_pleb, question_title, question_uuid,
                         tags=None):
    '''
    This task calls the util to create a question, if the util fails the
    task respawns itself.

    ERROR: For some reason when we expect the function to return False
        while testing it will sometimes return:
            TypeError("'DoesNotExist' object is not callable",)
        We don't know why but we must handle it

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
            If the create_question_util succeeds return True

            if fail retries creating the task
    '''
    if tags is None:
        tags = []
    else:
        tags = tags.split(',')
        
    question = create_question_util(content=content,
                                    question_title=question_title,
                                    question_uuid=question_uuid)
    if isinstance(question, Exception) is True:
        raise create_question_task.retry(exc=question, countdown=5,
                                         max_retries=None)

    task_data = {"question": question, "tags": tags}
    spawned = spawn_task(task_func=add_tags_to_question_task,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise create_question_task.retry(exc=spawned,
                                         countdown=3, max_retries=None)

    relations_data = {'sb_object': question, 'current_pleb': current_pleb}
    spawned = spawn_task(task_func=create_object_relations_task,
                         task_param=relations_data)
    return spawned


