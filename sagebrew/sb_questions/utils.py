import pytz
import traceback
from uuid import uuid1
from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from api.tasks import add_object_to_search_index
from api.utils import spawn_task
from plebs.neo_models import Pleb
from .neo_models import SBQuestion

def create_question_util(content="", current_pleb="", question_title="",tags=""):
    '''
    This util creates the question and attaches it to the user who asked it

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
    '''
    try:
        if content == "" or question_title == "":
            return None
        poster = Pleb.index.get(email=current_pleb)
        my_question = SBQuestion(content=content, question_title=question_title,
                                 question_id=str(uuid1()))
        my_question.save()
        search_dict = {'question_content': my_question.content, 'user': current_pleb,
                       'question_title': my_question.question_title, 'tags': tags,
                       'question_uuid': my_question.question_id,
                       'post_date': my_question.date_created,
                       'related_user': ''}
        search_data = {'object_type': 'question', 'object_data': search_dict}
        spawn_task(task_func=add_object_to_search_index, task_param=search_data, countdown=1)
        rel = my_question.owned_by.connect(poster)
        rel.save()
        rel_from_pleb = poster.questions.connect(my_question)
        rel_from_pleb.save()
        return my_question
    except Exception, e:
        print e
        return None

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
            owner = questions.traverse('owned_by').run()[0]
            owner_name = owner.first_name + ' ' + owner.last_name
            owner_profile_url = settings.WEB_ADDRESS + '/user/' + owner.email
            answers = questions.traverse('answer').where('to_be_deleted', '=',
                                                         False).run()
            for answer in answers:
                answer_owner = answer.traverse('owned_by').run()[0]
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
                owner = question.traverse('owned_by').run()[0]
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
    except Exception, e:
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
        question = SBQuestion.index.get(question_id=question_uuid)
        response = prepare_get_question_dictionary(question, sort_by='uuid',
                                                   current_pleb=current_pleb)
        return response
    except SBQuestion.DoesNotExist:
        traceback.print_exc()
        return {"detail": "There are no questions with that ID"}
    except Exception, e:
        traceback.print_exc()
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
        question_category = SBQuestion.category()
        questions = question_category.traverse('instance').where('to_be_deleted',
            '=', False).order_by_desc('date_created').skip(range_start).limit(
            range_end).run()
        return_dict = prepare_get_question_dictionary(questions,
                                                      sort_by='most recent',
                                                      current_pleb=current_pleb)
        return return_dict
    except Exception, e:
        traceback.print_exc()
        print e
        return {"detail": e}

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
        question_category = SBQuestion.category()
        questions = question_category.traverse('instance').where('to_be_deleted',
            '=', False).order_by('date_created').skip(range_start).limit(
            range_end).run()
        return_dict = prepare_get_question_dictionary(questions,
                                                      sort_by='most recent',
                                                      current_pleb=current_pleb)
        return return_dict
    except Exception, e:
        traceback.print_exc()
        print e
        return {"detail": "fail"}


def get_question_by_user():
    '''
    Sorting util

    This function gets questions between the range_start and range_end parameters,
    calls the util to create the dictionary of info the html to render then returns
    all the question posted by the specified user

    :param range_start:
    :param range_end:
    :param current_pleb:
    :return:
    '''
    pass

def get_question_by_tag():
    '''
    Sorting util

    This function gets questions between the range_start and range_end parameters,
    calls the util to create the dictionary of info the html to render then returns
    all the question posted by the specified tag

    :param range_start:
    :param range_end:
    :param current_pleb:
    :return:
    '''
    pass

def upvote_question_util(quesiton_uuid="", current_pleb=""):
    '''
    This util creates an upvote attached to the user who upvoted and
    the question that was upvoted

    :param quesiton_uuid:
    :param current_pleb:
    :return:
    '''
    from sb_questions.tasks import vote_question_task
    try:
        pleb = Pleb.index.get(email=current_pleb)
        my_question = SBQuestion.index.get(question_id=quesiton_uuid)
        my_question.up_vote_number += 1
        my_question.up_voted_by.connect(pleb)
        my_question.save()
        return True
    except SBQuestion.DoesNotExist:
        data = {'question_uuid': quesiton_uuid, 'current_pleb': current_pleb,
                'vote_type': 'up'}
        spawn_task(task_func=vote_question_task, task_param=data, countdown=1)
        return False
    except Pleb.DoesNotExist:
        return False

def downvote_question_util(quesiton_uuid="", current_pleb=""):
    '''
    This util creates an downvote attached to the user who downvote and
    the question that was downvote

    :param quesiton_uuid:
    :param current_pleb:
    :return:
    '''
    from sb_questions.tasks import vote_question_task
    try:
        pleb = Pleb.index.get(email=current_pleb)
        my_question = SBQuestion.index.get(question_id=quesiton_uuid)
        my_question.down_vote_number += 1
        my_question.down_voted_by.connect(pleb)
        my_question.save()
        return True
    except SBQuestion.DoesNotExist:
        data = {'question_uuid': quesiton_uuid, 'current_pleb': current_pleb,
                'vote_type': 'down'}
        spawn_task(task_func=vote_question_task, task_param=data, countdown=1)
        return False
    except Pleb.DoesNotExist:
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
        my_question = SBQuestion.index.get(question_id=question_uuid)
        if my_question.to_be_deleted:
            return {'question': my_question, 'detail': 'to be deleted'}

        if my_question.content == content:
            return {'question': my_question, 'detail': 'same content'}

        if my_question.last_edited_on == last_edited_on:
            return {'question': my_question, 'detail': 'same timestamp'}

        try:
            if my_question.last_edited_on > last_edited_on:
                return{'question': my_question, 'detail': 'last edit more recent'}
        except:
            pass

        my_question.content = content
        my_question.last_edited_on = last_edited_on
        my_question.save()
        return True
    except SBQuestion.DoesNotExist:
        return False

def prepare_question_search_html(question_uuid=str(uuid1())):
    my_question = SBQuestion.index.get(question_id=question_uuid)
    owner = my_question.traverse('owned_by').run()[0]
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