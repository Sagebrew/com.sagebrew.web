import pytz
import logging
from uuid import uuid1
from datetime import datetime
from urllib2 import HTTPError
from requests import ConnectionError
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import (api_view, permission_classes)

from api.utils import (get_post_data, spawn_task, post_to_api)
from plebs.neo_models import Pleb
from .utils import (get_question_by_most_recent, get_question_by_tag,
                    get_question_by_user, get_question_by_uuid,
                    get_question_by_least_recent)
from .tasks import create_question_task
from .forms import SaveQuestionForm, EditQuestionForm

logger = logging.getLogger('loggly_logs')

@login_required()
def submit_question_view_page(request):
    '''
    This is the view that creates the page which displays the html to create
    a question

    :param request:
    :return:
    '''
    current_user = request.user
    return render(request,'save_question.html',{
        'current_user': current_user.email,
    })

@login_required()
def question_page(request, sort_by="most_recent"):
    '''
    This is the page that displays what is returned from the get_question_view
    api endpoint

    Only pass 'question_uuid' parameter if you want to get a single question
    that matched the uuid. This will most likely occur when clicking on a
    question which is shown on your newsfeed or another page

    :param request:
                request.DATA/request.body = {
                    'question_uuid': str(uuid1()),
                    'current_pleb': 'example@email.com'
                    'sort_by': ''
                }
    :return:
    '''
    current_user = request.user
    post_data = {'current_pleb': current_user.email,
                 'sort_by': sort_by}
    headers = {'content-type': 'application/json'}
    questions = post_to_api(reverse('get_questions'), data=post_data,
                            headers=headers)
    return render(request, 'question.html', {'questions': questions})

@login_required()
def question_detail_page(request, question_uuid=str(uuid1())):
    '''
    This is the view that displays a single question with all answers, comments,
    references and tags.
    :param request:
    :return:
    '''
    current_user = request.user
    post_data = {'current_pleb': current_user.email,
                 'sort_by': 'uuid',
                 'question_uuid': question_uuid}
    headers = {'content-type': 'application/json'}
    question = post_to_api(reverse('get_questions'), data=post_data,
                           headers=headers)
    return render(request, 'question_detail.html', {'question': question})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_question_view(request):
    '''
    Allows the user to create a question

    :param request:
            request.DATA or request.body = {
                'content': '',
                'current_pleb': 'example@email.com'
                'question_title': ''
            }
    :return:
    '''
    try:
        question_data = get_post_data(request)
        if type(question_data) != dict:
            return Response({"details": "Please provide a valid JSON object"},
                            status=400)
        #question_data['content'] = language_filter(question_data['content'])
        question_form = SaveQuestionForm(question_data)
        if question_form.is_valid():
            spawn_task(task_func=create_question_task,
                       task_param=question_form.cleaned_data)
            return Response({"detail": "filtered",
                             "filtered_content": question_data}, status=200)
        else:
            return Response(question_form.errors, status=400)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create question"})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def edit_question_view(request):
    '''
    Allows the owner/admin to edit the question

    :param request:
            request.DATA/request.body = {
                'question_uuid': str(uuid1())
                'content': '',
                'current_pleb': 'example@email.com',
                'last_edited_on': datetime
            }
    :return:
    '''
    try:
        question_data = get_post_data(request)
        if type(question_data) != dict:
            return Response({"details": "Please provide a valid JSON object"},
                            status=400)
        try:
            question_data['last_edited_on'] = datetime.now(pytz.utc)
        except TypeError:
            question_data = question_data

        question_form = EditQuestionForm(question_data)
        if question_form.is_valid():
            #spawn_task(task_func=edit_question_task,
            #            question_form.cleaned_data)
            return Response({"detail": "edit question task spawned"},
                            status=200)
        else:
             return Response(question_form.errors, status=400)

    except (HTTPError, ConnectionError):
        return Response({'detail': 'failed to edit'}, status=400)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def close_question_view(request):
    '''
    Allows admins to close questions. If the question is irrelevant or redundant
    or the question is no longer active

    :param request:
            request.DATA/request.body = {
                'question_uuid': str(uuid1()),
                'current_pleb': 'example@email.com'
            }
    :return:
    '''
    pass

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_question_view(request):
    '''
    Only to be used by admins once it has been voted that the question should
    be deleted

    :param request:
    :return:
    '''
    pass

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def vote_question_view(request):
    '''
    Allows the user to upvote/downvote question

    :param request:
            request.DATA/request.body = {
                'question_uuid': str(uuid1()),
                'vote_type': 'up' or 'down',
                'current_pleb': 'example@email.com'
    :return:
    '''
    pass

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_question_view(request):
    '''
    Gets the question/questions.

    Accepted 'sort_by' parameters:
                                  'uuid',
                                  'most_recent',
                                  'least_recent',
                                  'tag',
                                  'user',
                                  'top_rated',
                                  'trending_yearly',
                                  'trending_monthly',
                                  'trending_weekly',
                                  'trending_daily',
                                  'most_relevant',
                                  'keyword'

    The 'question_uuid' parameter is only required if you want to retrieve one
        question, also if the uuid is passed range_start and range_end will
        be ignored

    The 'user' parameter is only required if you want to retrieve all questions
        from a user This will occur mostly if you navigate from a users profile
        to their questions

    The most_relevant parameter is based upon the current_plebs selected
        interests

    :param request:
            request.DATA/request.body = {
                'question_uuid': str(uuid1()),
                'user': 'example2@email.com',
                'current_pleb': 'example@email.com',
                'sort_by': '',
                'range_start': 0,
                'range_end': 5
            }
    :return:
    '''
    question_data = get_post_data(request)
    print question_data
    if question_data['sort_by'] == 'most_recent':
        response = get_question_by_most_recent()
    elif question_data['sort_by'] == 'uuid':
        response = get_question_by_uuid(question_data['question_uuid'])
    elif question_data['sort_by'] == 'least_recent':
        response = get_question_by_least_recent()
    else:
        response = {"detail": "fail"}
    return Response(response)