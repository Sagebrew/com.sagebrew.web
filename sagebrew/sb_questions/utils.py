from uuid import uuid1
from textblob import TextBlob

from neomodel import DoesNotExist, CypherException

from api.utils import execute_cypher_query
from .neo_models import SBQuestion
from sb_base.decorators import apply_defense


@apply_defense
def create_question_util(content, question_title, question_uuid):
    '''
    This util creates the question and attaches it to the user who asked it

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
    '''
    try:
        question = SBQuestion.nodes.get(sb_id=question_uuid)
    except (SBQuestion.DoesNotExist, DoesNotExist):
        content_blob = TextBlob(content)
        title_blob = TextBlob(question_title)
        question = SBQuestion(content=content,
                              question_title=question_title,
                              sb_id=question_uuid)
        question.subjectivity = content_blob.subjectivity
        question.positivity = content_blob.polarity
        question.title_polarity = title_blob.polarity
        question.title_subjectivity = title_blob.subjectivity
        question.save()
    except CypherException as e:
        return e
    return question


@apply_defense
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
        return False
    except CypherException as e:
        return e


@apply_defense
def get_question_by_most_recent(range_start=0, range_end=5):
    '''
    Sorting util

    This function gets questions between the range_start and range_end parameters,
    calls the util to create the dictionary of info the html to render then returns
    with the questions ordered from most recent to least recent

    :param range_start:
    :param range_end:
    :return:
    '''
    query = 'match (q:SBQuestion) where q.to_be_deleted=False ' \
            'with q order by q.date_created desc ' \
            'with q skip %s limit %s ' \
            'return q' % (range_start, range_end)
    questions, meta = execute_cypher_query(query)
    questions = [SBQuestion.inflate(row[0]) for row in questions]
    return questions


@apply_defense
def get_question_by_least_recent(range_start=0, range_end=5):
    '''
    Sorting util

    This function gets questions between the range_start and range_end parameters,
    calls the util to create the dictionary of info the html to render then returns
    with the questions ordered from least recent to more recent

    :param range_start:
    :param range_end:
    :return:
    '''
    query = 'match (q:SBQuestion) where q.to_be_deleted=False ' \
            'with q order by q.date_created ' \
            'with q skip %s limit %s ' \
            'return q' % (range_start, range_end)
    questions, meta = execute_cypher_query(query)
    if isinstance(questions, Exception):
        # TODO might want to handle differently
        return questions
    # TODO couldn't questions be None or empty here? do we have a handler
    # for that?
    questions = [SBQuestion.inflate(row[0]) for row in questions]
    return questions


@apply_defense
def prepare_question_search_html(question_uuid):
    try:
        my_question = SBQuestion.nodes.get(sb_id=question_uuid)
    except (SBQuestion.DoesNotExist, DoesNotExist):
        return False
    except CypherException:
        return None

    return my_question.render_search()
