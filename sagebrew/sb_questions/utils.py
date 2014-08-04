import pytz
import traceback
from uuid import uuid1
from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse

from api.utils import spawn_task
from plebs.neo_models import Pleb
from .neo_models import SBQuestion

def create_question_util(content="", current_pleb="", question_title=""):
    '''

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
    '''
    try:
        poster = Pleb.index.get(email=current_pleb)
        my_question = SBQuestion(content=content, question_title=question_title,
                                 question_id=str(uuid1()))
        my_question.save()
        rel = my_question.owned_by.connect(poster)
        rel.save()
        rel_from_pleb = poster.questions.connect(my_question)
        rel_from_pleb.save()
        return my_question
    except:
        return None

def prepare_get_question_dictionary(questions, sort_by):
    #TODO generate a url to have a redirect to a page with one question along
    #with comments and answers
    question_array = []

    if sort_by == 'uuid':
        owner = questions.traverse('owned_by').run()[0]
        owner_name = owner.first_name + ' ' + owner.last_name
        owner_profile_url = settings.WEB_ADDRESS + '/user/' + owner.email
        answers = questions.traverse('answer').where('to_be_deleted', '=',
                                                     False).run()
        question_dict = {'question_title': questions.question_title,
                         'question_content': questions.content,
                         'is_closed': questions.is_closed,
                         'answer_number': questions.answer_number,
                         'last_edited_on': questions.last_edited_on,
                         'up_vote_number': questions.up_vote_number,
                         'down_vote_number': questions.down_vote_number,
                         'owner': owner_name,
                         'owner_profile_url': owner_profile_url,
                         'time_created': questions.date_created,
                         'answers': answers}
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
                                             '/questions/uuid/' +
                                             question.question_id
                        }
            question_array.append(question_dict)
        return question_array

def get_question_by_uuid(question_uuid=str(uuid1())):
    try:
        question = SBQuestion.index.get(question_id=question_uuid)
        response = prepare_get_question_dictionary(question, sort_by='uuid')
        return response
    except SBQuestion.DoesNotExist:
        print 'fail'
        traceback.print_exc()
        print question_uuid
        return {"detail": "There are no questions with that ID"}
    except Exception, e:
        print e
        traceback.print_exc()
        return {"detail": "Failure"}

def get_question_by_most_recent(range_start=0, range_end=5):
    try:
        question_category = SBQuestion.category()
        questions = question_category.traverse('instance').where('to_be_deleted',
            '=', False).order_by_desc('date_created').skip(range_start).limit(
            range_end).run()
        return_dict = prepare_get_question_dictionary(questions,
                                                      sort_by='most recent')
        return return_dict
    except Exception, e:
        traceback.print_exc()
        print e
        return {"detail": e}

def get_question_by_least_recent(range_start=0, range_end=5):
    try:
        question_category = SBQuestion.category()
        questions = question_category.traverse('instance').where('to_be_deleted',
            '=', False).order_by('date_created').skip(range_start).limit(
            range_end).run()
        return_dict = prepare_get_question_dictionary(questions,
                                                      sort_by='most recent')
        return return_dict
    except Exception, e:
        traceback.print_exc()
        print e
        return {"detail": "fail"}


def get_question_by_user():
    pass

def get_question_by_tag():
    pass

