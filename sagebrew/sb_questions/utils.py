from textblob import TextBlob

from django.template.loader import render_to_string

from neomodel import DoesNotExist, CypherException

from api.utils import execute_cypher_query
from sb_base.decorators import apply_defense

from .neo_models import SBQuestion


@apply_defense
def create_question_util(content, title, question_uuid):
    '''
    This util creates the question and attaches it to the user who asked it

    :param content:
    :param current_pleb:
    :param title:
    :return:
    '''
    try:
        question = SBQuestion.nodes.get(object_uuid=question_uuid)
    except (SBQuestion.DoesNotExist, DoesNotExist):
        content_blob = TextBlob(content)
        title_blob = TextBlob(title)
        question = SBQuestion(content=content,
                              title=title,
                              object_uuid=question_uuid)
        question.subjectivity = content_blob.subjectivity
        question.positivity = content_blob.polarity
        question.title_polarity = title_blob.polarity
        question.title_subjectivity = title_blob.subjectivity
        question.save()
    except CypherException as e:
        return e
    return question


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
    query = 'match (q:SBQuestion) where q.to_be_deleted=False and q.original=True ' \
            'with q order by q.created desc ' \
            'with q skip %s limit %s ' \
            'return q' % (range_start, range_end)
    questions, meta = execute_cypher_query(query)
    if isinstance(questions, Exception):
        return questions
    try:
        questions = [SBQuestion.inflate(row[0]) for row in questions]
    except IndexError:
        questions = []
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
    query = 'match (q:SBQuestion) where q.to_be_deleted=False and q.original=True ' \
            'with q order by q.created ' \
            'with q skip %s limit %s ' \
            'return q' % (range_start, range_end)
    questions, meta = execute_cypher_query(query)
    if isinstance(questions, Exception):
        return questions
    try:
        questions = [SBQuestion.inflate(row[0]) for row in questions]
    except IndexError:
        questions = []
    return questions


@apply_defense
def get_question_by_recent_edit(range_start=0, range_end=5):
    query = 'match (q:SBQuestion) where q.to_be_deleted=False and q.original=True ' \
            'with q order by q.last_edited_on desc ' \
            'with q skip %s limit %s ' \
            'return q' % (range_start, range_end)
    questions, meta = execute_cypher_query(query)
    if isinstance(questions, Exception):
        return questions
    try:
        questions = [SBQuestion.inflate(row[0]) for row in questions]
    except IndexError:
        questions = []
    return questions


@apply_defense
def prepare_question_search_html(question_uuid, request):
    try:
        my_question = SBQuestion.nodes.get(object_uuid=question_uuid)
    except (SBQuestion.DoesNotExist, DoesNotExist):
        return False
    except CypherException:
        return None

    return my_question.render_search(request)


def render_question_object(question_object):
    return render_to_string('question.html', question_object)