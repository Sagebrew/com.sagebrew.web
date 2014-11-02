import logging
from uuid import uuid1
from json import dumps
from celery import shared_task
from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task, create_auto_tags
from api.tasks import add_object_to_search_index
from plebs.neo_models import Pleb

from sb_tag.tasks import add_auto_tags, add_tags
from .neo_models import SBQuestion
from .utils import (create_question_util, edit_question_util)

logger = logging.getLogger('loggly_logs')



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
        if question.added_to_search_index:
            return True
        else:
            search_dict = {'question_content': question.content,
                           'user': question.owned_by.all()[0].email,
                           'question_title': question.question_title,
                           'tags': tags,
                           'question_uuid': question.sb_id,
                           'post_date': question.date_created,
                           'related_user': ''}
            task_data = {"object_type": "question",
                         "object_data": search_dict}
            question.added_to_search_index = True
            question.save()
            spawn_task(task_func=add_object_to_search_index,
                              task_param=task_data)
            return True

    except IndexError as e:
        raise add_question_to_indices_task.retry(exc=e, countdown=3,
                                                 max_retries=None)
    except CypherException as e:
        raise add_question_to_indices_task.retry(exc=e,
                                                 countdown=3, max_retries=None)
    except Exception as e:
        logger.exception(dumps(
            {
                "function": add_question_to_indices_task.__name__,
                "exception": "UnhandledException"
            }))
        raise add_question_to_indices_task.retry(exc=e, countdown=3,
                                                 max_retries=None)

@shared_task()
def add_tags_to_question_task(question, tags):
    '''
    This function will take a question object, a list of
    tags and auto tags and manage the other tasks which attach them to
    the question.

    :param question:
    :param tags:
    :param auto_tags:
    :return:
    '''
    try:
        if question.tags_added:
            task_data = {
                'question': question,
                'tags': tags
            }
            return spawn_task(task_func=add_question_to_indices_task,
                              task_param=task_data)
        else:
            auto_tags = create_auto_tags(question.content)
            task_data = []
            for tag in auto_tags['keywords']:
                task_data.append({"tags": tag,
                                  "object_uuid": question.sb_id,
                                  "object_type": "question"
                })
            tag_list = {'tag_list': task_data}
            tag_task_data = {"object_uuid": question.sb_id,
                             "object_type": "question", "tags": tags}
            spawn_task(task_func=add_tags, task_param=tag_task_data)
            spawn_task(task_func=add_auto_tags, task_param=tag_list)
            question.tags_added = True
            question.save()
            return spawn_task(task_func=add_tags_to_question_task,
                              task_param={'question': question, 'tags': tags})
    except CypherException as e:
        raise add_tags_to_question_task.retry(exc=e, countdown=3,
                                              max_retries=None)
    except Exception as e:
        logger.exception(dumps({"function": add_tags_to_question_task.__name__,
                                "exception": "UnhandledException: "}))
        raise add_tags_to_question_task.retry(exc=e, countdown=3,
                                              max_retries=None)



@shared_task()
def create_question_task(content="", current_pleb="", question_title="",
                         question_uuid=str(uuid1()), tags="", **kwargs):
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
    tag_list = tags.split(',')
    try:
        try:
            SBQuestion.nodes.get(sb_id=question_uuid)
            return False
        except (SBQuestion.DoesNotExist, DoesNotExist):
            response = create_question_util(content=content,
                                            current_pleb=current_pleb,
                                            question_title=question_title)
        if isinstance(response, Exception) is True:
            raise create_question_task.retry(exc=response, countdown=5,
                                             max_retries=None)
        elif response is None:
            return False
        else:
            task_data = {"question": response, "tags": tags}
            return spawn_task(task_func=add_tags_to_question_task,
                              task_param=task_data)
    except CypherException as e:
        raise create_question_task.retry(exc=e, countdown=3, max_retries=None)
    except Exception as e:
        logger.exception({'function': create_question_task.__name__,
                          'exception': "UnhandledException: "})
        raise create_question_task.retry(exc=e, countdown=5, max_retries=None)


@shared_task()
def edit_question_task(question_uuid="", content="", current_pleb="",
                       last_edited_on=""):
    '''
    This task calls the util which determines if a question can be edited or not
    returns True and False based on how the util responds

    :param question_uuid:
    :param content:
    :param current_pleb:
    :param last_edited_on:
    :return:
    '''
    try:
        try:
            Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False
        try:
            SBQuestion.nodes.get(sb_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist) as e:
            raise edit_question_task.retry(exc=e, countdown=3, max_retries=None)
        edit_question_return = edit_question_util(question_uuid=question_uuid,
                                                  content=content,
                                                  current_pleb=current_pleb,
                                                  last_edited_on=last_edited_on)
        if edit_question_return == True:
            return True
        if edit_question_return['detail'] == 'to be deleted':
            return False
        elif edit_question_return['detail'] == 'same content':
            return False
        elif edit_question_return['detail'] == 'same timestamp':
            return False
        elif edit_question_return['detail'] == 'last edit more recent':
            return False
    except CypherException as e:
        raise edit_question_task.retry(exc=e, countdown=3, max_retries=None)
    except Exception as e:
        logger.exception({"function": edit_question_task.__name__,
                          "exception": "UnhandledException: "})
        raise edit_question_task.retry(exc=e, countdown=3, max_retries=None)
