import logging
import traceback
from uuid import uuid1
from json import dumps
from textblob import TextBlob

from neomodel import DoesNotExist, CypherException
from django.conf import settings
from django.template.loader import render_to_string

from api.utils import execute_cypher_query, spawn_task
from sb_base.tasks import create_object_relations_task
from plebs.neo_models import Pleb
from sb_answers.neo_models import SBAnswer
from .neo_models import SBQuestion

logger = logging.getLogger('loggly_logs')


def create_question_util(content, current_pleb, question_title,
                         question_uuid=None):
    '''
    This util creates the question and attaches it to the user who asked it

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
    '''
    if question_uuid is None:
        question_uuid = str(uuid1())
    try:
        try:
            poster = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False

        content_blob = TextBlob(content)
        title_blob = TextBlob(question_title)
        my_question = SBQuestion(content=content,
                                 question_title=question_title,
                                 sb_id=question_uuid)
        my_question.save()
        my_question.subjectivity = content_blob.subjectivity
        my_question.positivity = content_blob.polarity
        my_question.title_polarity = title_blob.polarity
        my_question.title_subjectivity = title_blob.subjectivity
        my_question.save()
        relations_data = {'sb_object': my_question, 'current_pleb': poster}
        spawn_task(task_func=create_object_relations_task,
                   task_param=relations_data)
        return my_question
    except CypherException as e:
        return e
    except Exception as e:
        logger.exception(dumps({"function": create_question_util.__name__,
                                'exception': "Unhandled Exception"}))
        return e


def get_question_by_uuid(question_uuid, current_pleb):
    '''
    Sorting util

    This function gets a question by a uuid. It calls prepare_get_question_dictionary
    to create the dictionary of question details and answer details then returns
    to the view

    :param question_uuid:
    :param current_pleb:
    :return:
    '''
    try:
        question = SBQuestion.nodes.get(sb_id=question_uuid)
        return question.render_single(current_pleb)
    except (SBQuestion.DoesNotExist, DoesNotExist):
        return {"detail": "There are no questions with that ID"}
    except CypherException:
        return {"detail": "A CypherException was thrown"}
    except Exception:
        logger.exception(dumps({"function": get_question_by_uuid.__name__,
                                "exception": "Unhandled Exception"}))
        return {"detail": "Failure"}


def get_question_by_most_recent(current_pleb, range_start=0, range_end=5):
    '''
    Sorting util

    This function gets questions between the range_start and range_end parameters,
    calls the util to create the dictionary of info the html to render then returns
    with the questions ordered from most recent to least recent

    :param range_start:
    :param range_end:
    :param current_pleb:
    :return:
    '''
    try:
        query = 'match (q:SBQuestion) where q.to_be_deleted=False ' \
                'with q order by q.date_created desc ' \
                'with q skip %s limit %s ' \
                'return q' % (range_start, range_end)
        questions, meta = execute_cypher_query(query)
        questions = [SBQuestion.inflate(row[0]) for row in questions]
        return questions
    except Exception:
        logger.exception(dumps({"function": get_question_by_most_recent.__name__,
                                "exception": "Unhandled Exception"}))
        return {"detail": "fail"}


def get_question_by_least_recent(current_pleb, range_start=0, range_end=5):
    '''
    Sorting util

    This function gets questions between the range_start and range_end parameters,
    calls the util to create the dictionary of info the html to render then returns
    with the questions ordered from least recent to more recent

    :param range_start:
    :param range_end:
    :param current_pleb:
    :return:
    '''
    try:
        query = 'match (q:SBQuestion) where q.to_be_deleted=False ' \
                'with q order by q.date_created ' \
                'with q skip %s limit %s ' \
                'return q' % (range_start, range_end)
        questions, meta = execute_cypher_query(query)
        questions = [SBQuestion.inflate(row[0]) for row in questions]
        return questions
    except Exception:
        logger.exception(dumps(
            {"function": get_question_by_least_recent.__name__,
             "exception": "Unhandled Exception"}))
        return {"detail": "fail"}

def prepare_question_search_html(question_uuid):
    try:
        try:
            my_question = SBQuestion.nodes.get(sb_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist):
            return False

        return my_question.render_search()

    except IndexError:
        return False
    except Exception:
        logger.exception(dumps(
            {"function": prepare_question_search_html.__name__,
             "exception": "Unhandled Exception"}))
        return False
