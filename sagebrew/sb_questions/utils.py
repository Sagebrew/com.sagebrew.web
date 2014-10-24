import logging
from uuid import uuid1
from json import dumps
from textblob import TextBlob

from neomodel import DoesNotExist, UniqueProperty, CypherException
from django.conf import settings
from django.template.loader import render_to_string

from api.tasks import add_object_to_search_index
from api.utils import spawn_task, create_auto_tags, execute_cypher_query
from plebs.neo_models import Pleb
from sb_answers.neo_models import SBAnswer
from .neo_models import SBQuestion
from sb_tag.tasks import add_auto_tags, add_tags

logger = logging.getLogger('loggly_logs')

def create_question_util(content="", current_pleb="", question_title=""):
    '''
    This util creates the question and attaches it to the user who asked it

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
    '''
    task_data = []
    try:
        if content == "" or question_title == "":
            return None
        try:
            poster = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return None

        content_blob = TextBlob(content)
        title_blob = TextBlob(question_title)
        my_question = SBQuestion(content=content,
                                 question_title=question_title,
                                 question_id=str(uuid1()))
        my_question.save()
        my_question.subjectivity = content_blob.subjectivity
        my_question.positivity = content_blob.polarity
        my_question.title_polarity = title_blob.polarity
        my_question.title_subjectivity = title_blob.subjectivity
        rel = my_question.owned_by.connect(poster)
        rel.save()
        rel_from_pleb = poster.questions.connect(my_question)
        rel_from_pleb.save()
        return my_question
    except CypherException:
        return False
    except Exception:
        logger.exception({"function": create_question_util.__name__,
                          'exception': "UnhandledException: "})
        return False

def prepare_get_question_dictionary(questions, sort_by, current_pleb=""):
    '''
    This util creates the dictionary responses which are returned to the html
    files. It is universal and will handle any sorting parameter

    Returns dictionaries containing the data .html files require to render
    questions and, if it is a single question page, all the answers to the question

    :param questions:
    :param sort_by:
    :param current_pleb:
    :return:
    '''
    question_array = []
    answer_array = []
    try:
        if sort_by == 'uuid':
            owner = questions.owned_by.all()
            owner = owner[0]
            owner_name = owner.first_name + ' ' + owner.last_name
            owner_profile_url = settings.WEB_ADDRESS + '/user/' + owner.email
            query = 'match (q:SBQuestion) where q.question_id="%s" ' \
                    'with q ' \
                    'match (q)-[:POSSIBLE_ANSWER]-(a:SBAnswer) ' \
                    'where a.to_be_deleted=False ' \
                    'return a ' % questions.question_id
            answers, meta = execute_cypher_query(query)
            answers = [SBAnswer.inflate(row[0]) for row in answers]
            for answer in answers:
                answer_owner = answer.owned_by.all()[0]
                answer_owner_name = answer_owner.first_name +' '+answer_owner.last_name
                answer_owner_url = settings.WEB_ADDRESS+'/user/'+owner.email
                answer_dict = {'answer_content': answer.content,
                               'current_pleb': current_pleb,
                               'answer_uuid': answer.answer_id,
                               'last_edited_on': answer.last_edited_on,
                               'up_vote_number': answer.up_vote_number,
                               'down_vote_number': answer.down_vote_number,
                               'answer_owner_name': answer_owner_name,
                               'answer_owner_url': answer_owner_url,
                               'time_created': answer.date_created,
                               'answer_owner_email': answer_owner.email}
                answer_array.append(answer_dict)
            question_dict = {'question_title': questions.question_title,
                             'question_content': questions.content,
                             'question_uuid': questions.question_id,
                             'is_closed': questions.is_closed,
                             'answer_number': questions.answer_number,
                             'last_edited_on': questions.last_edited_on,
                             'up_vote_number': questions.up_vote_number,
                             'down_vote_number': questions.down_vote_number,
                             'owner': owner_name,
                             'owner_profile_url': owner_profile_url,
                             'time_created': questions.date_created,
                             'answers': answer_array,
                             'current_pleb': current_pleb,
                             'owner_email': owner.email}
            return question_dict
        else:
            for question in questions:
                owner = question.owned_by.all()
                owner = owner[0]
                owner = owner.first_name + ' ' + owner.last_name
                question_dict = {'question_title': question.question_title,
                                 'question_content': question.content[:50]+'...',
                                 'is_closed': question.is_closed,
                                 'answer_number': question.answer_number,
                                 'last_edited_on': question.last_edited_on,
                                 'up_vote_number': question.up_vote_number,
                                 'down_vote_number': question.down_vote_number,
                                 'owner': owner,
                                 'time_created': question.date_created,
                                 'question_url': settings.WEB_ADDRESS +
                                                 '/questions/' +
                                                 question.question_id,
                                 'current_pleb': current_pleb
                            }
                question_array.append(question_dict)
            return question_array
    except IndexError:
        return []
    except Exception:
        logger.exception(dumps({"function": prepare_get_question_dictionary.__name__,
                                "exception": "UnhandledException: "}))
        return []

def get_question_by_uuid(question_uuid=str(uuid1()), current_pleb=""):
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
        question = SBQuestion.nodes.get(question_id=question_uuid)
        response = prepare_get_question_dictionary(question, sort_by='uuid',
                                                   current_pleb=current_pleb)
        return response
    except (SBQuestion.DoesNotExist, DoesNotExist):
        return {"detail": "There are no questions with that ID"}
    except CypherException:
        return {"detail": "A CypherException was thrown"}
    except Exception:
        logger.exception(dumps({"function": get_question_by_uuid.__name__,
                                "exception": "UnhandledException: "}))
        return {"detail": "Failure"}

def get_question_by_most_recent(range_start=0, range_end=5, current_pleb=""):
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
        return_dict = prepare_get_question_dictionary(questions,
                                                      sort_by='most recent',
                                                      current_pleb=current_pleb)
        return return_dict
    except Exception:
        logger.exception(dumps({"function": get_question_by_most_recent.__name__,
                                "exception": "UnhandledException: "}))
        return {"detail": "fail"}

def get_question_by_least_recent(range_start=0, range_end=5, current_pleb=""):
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
        return_dict = prepare_get_question_dictionary(questions,
                                                      sort_by='most recent',
                                                      current_pleb=current_pleb)
        return return_dict
    except Exception:
        logger.exception(dumps({"function": get_question_by_least_recent.__name__,
                                "exception": "UnhandledException: "}))
        return {"detail": "fail"}


def upvote_question_util(question_uuid="", current_pleb=""):
    '''
    This util creates an upvote attached to the user who upvoted and
    the question that was upvoted

    :param quesiton_uuid:
    :param current_pleb:
    :return:
    '''
    from sb_questions.tasks import vote_question_task
    try:
        try:
            pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return None
        try:
            my_question = SBQuestion.nodes.get(question_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist):
            return False

        my_question.up_vote_number += 1
        my_question.up_voted_by.connect(pleb)
        my_question.save()
        return True
    except CypherException:
        return False
    except Exception:
        logger.exception({"function": upvote_question_util.__name__,
                          "exception:":"UnhandledException: "})
        return False

def downvote_question_util(question_uuid="", current_pleb=""):
    '''
    This util creates an downvote attached to the user who downvote and
    the question that was downvote

    :param quesiton_uuid:
    :param current_pleb:
    :return:
    '''
    from sb_questions.tasks import vote_question_task
    try:
        try:
            pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return None
        try:
            my_question = SBQuestion.nodes.get(question_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist):
            return False
        my_question.down_vote_number += 1
        my_question.down_voted_by.connect(pleb)
        my_question.save()
        return True
    except CypherException:
        return False
    except Exception:
        logger.exception({"function": downvote_question_util.__name__,
                          "exception": "UnhandledException: "})
        return False

def edit_question_util(question_uuid="", content="", last_edited_on="",
                       current_pleb=""):
    '''
    This util handles the editing of a question. It does not edit the question
    if it is set to be deleted, the content it is trying to edit with is the
    same as the current content, the last time it was edited is the same as the
    current time, or if the last time is was edited was more recent than the
    current time. Succeeds in editing on all other scenarios

    :param question_uuid:
    :param content:
    :param last_edited_on:
    :param current_pleb:
    :return:
    '''
    try:
        try:
            my_question = SBQuestion.nodes.get(question_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist):
            return False
        if my_question.to_be_deleted:
            return {'question': my_question, 'detail': 'to be deleted'}

        if my_question.content == content:
            return {'question': my_question, 'detail': 'same content'}

        if my_question.last_edited_on == last_edited_on:
            return {'question': my_question, 'detail': 'same timestamp'}

        try:
            if my_question.last_edited_on > last_edited_on:
                return {'question': my_question, 'detail': 'last edit more recent'}
        except TypeError:
            pass

        edit_question = create_question_util(content=content, current_pleb=current_pleb,
                                             question_title=my_question.question_title)
        my_question.edits.connect(edit_question)
        edit_question.edit_to.connect(my_question)
        my_question.last_edited_on = edit_question.date_created
        my_question.save()
        return True
    except CypherException:
        return False
    except Exception:
        logger.exception({"function": edit_question_util.__name__,
                          "exception": "UnhandledException: "})
        return False

def prepare_question_search_html(question_uuid):
    try:
        try:
            my_question = SBQuestion.nodes.get(question_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist):
            return False
        owner = my_question.owned_by.all()[0]
        owner_name = owner.first_name + ' ' + owner.last_name
        owner_profile_url = settings.WEB_ADDRESS + '/user/' + owner.email
        question_dict = {"question_title": my_question.question_title,
                         "question_content": my_question.content,
                         "question_uuid": my_question.question_id,
                         "is_closed": my_question.is_closed,
                         "answer_number": my_question.answer_number,
                         "last_edited_on": my_question.last_edited_on,
                         "up_vote_number": my_question.up_vote_number,
                         "down_vote_number": my_question.down_vote_number,
                         "owner": owner_name,
                         "owner_profile_url": owner_profile_url,
                         "time_created": my_question.date_created,
                         "owner_email": owner.email}
        rendered = render_to_string('question_search.html', question_dict)
        return rendered

    except IndexError:
        return False

    except Exception:
        logger.exception({"function": prepare_question_search_html.__name__,
                          "exception": "UnhandledException: "})
        return False

def flag_question_util(question_uuid, current_pleb, flag_reason):
    '''
    This function will increase the flag count on any of the reasons
    that a question could be flagged and connect a user to the question
    showing that they have flagged the question already in case they
    attempt to flag it multiple times.

    :param question_uuid:
    :param current_pleb:
    :param flag_reason:
    :return:
    '''
    try:
        try:
            question = SBQuestion.nodes.get(question_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist):
            return False

        try:
            pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return None

        if question.flagged_by.is_connected(pleb):
            return True

        question.flagged_by.connect(pleb)
        if flag_reason == 'spam':
            question.flagged_as_spam_count += 1
            question.save()
        elif flag_reason == 'explicit':
            question.flagged_as_explicit_count += 1
            question.save()
        elif flag_reason == 'other':
            question.flagged_as_other_count += 1
            question.save()
        elif flag_reason == 'duplicate':
            question.flagged_as_duplicate_count += 1
            question.save()
        elif flag_reason == 'changed':
            question.flagged_as_changed_count += 1
            question.save()
        elif flag_reason == 'unsupported':
            question.flagged_as_unsupported_count += 1
            question.save()
        else:
            return False
        return True
    except Exception:
        logger.exception(dumps({"function": flag_question_util.__name__,
                                "exception": "UnhandledException: "}))
        return False