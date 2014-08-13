import pytz
import logging
from uuid import uuid1
from datetime import datetime
from urllib2 import HTTPError
from requests import ConnectionError
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import (api_view, permission_classes,
                                       renderer_classes)

from api.utils import (get_post_data, spawn_task, post_to_api)
from plebs.neo_models import Pleb
from .utils import (get_question_by_most_recent, get_question_by_tag,
                    get_question_by_user, get_question_by_uuid,
                    get_question_by_least_recent, prepare_question_search_html)
from .tasks import create_question_task, vote_question_task, edit_question_task
from .forms import SaveQuestionForm, EditQuestionForm, VoteQuestionForm

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
    return render(request, 'question_sort_page.html', {'questions': questions})

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
    This is the API view to create a question

    :param request:

            request.DATA or request.body = {
                'content': '',
                'current_pleb': 'example@email.com'
                'question_title': ''
            }

    :return:
    '''
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

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def edit_question_view(request):
    '''
   The API view to allow a user to edit their question

    :param request:

            request.DATA/request.body = {
                'question_uuid': str(uuid1())
                'content': '',
                'current_pleb': 'example@email.com',
                'last_edited_on': datetime
            }

    :return:
    '''
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
        spawn_task(task_func=edit_question_task,
                   task_param=question_form.cleaned_data)
        return Response({"detail": "edit question task spawned"},
                        status=200)
    else:
        return Response(question_form.errors, status=400)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def close_question_view(request):
    '''
    The API view to allow admins to close questions. If the question is
    irrelevant or redundant or the question is no longer active

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
def vote_question_view(request):
    '''
    The API view to allow the user to upvote/downvote question

    :param request:

            request.DATA/request.body = {
                'question_uuid': str(uuid1()),
                'vote_type': 'up' or 'down',
                'current_pleb': 'example@email.com'

    :return:
    '''
    try:
        post_data = get_post_data(request)
        if type(post_data) != dict:
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        question_form = VoteQuestionForm(post_data)
        if question_form.is_valid():
            spawn_task(task_func=vote_question_task,
                       task_param=question_form.cleaned_data)
            return Response({"detail": "Vote Created!"}, status=200)
        else:
            return Response({'detail': question_form.errors}, status=400)
    except Exception, e:
        return Response({"detail": "Vote could not be created!",
                         'exception': e})

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
    try:
        question_data = get_post_data(request)
        if question_data['sort_by'] == 'most_recent':
            response = get_question_by_most_recent(current_pleb=question_data['current_pleb'])
        elif question_data['sort_by'] == 'uuid':
            response = get_question_by_uuid(question_data['question_uuid'],
                                            question_data['current_pleb'])
        elif question_data['sort_by'] == 'least_recent':
            response = get_question_by_least_recent(current_pleb=question_data['current_pleb'])
        else:
            response = {"detail": "fail"}
            return Response(response, status=400)
        return Response(response, status=200)
    except Exception, e:
        return Response({'detail': 'fail'}, status=400)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_question_search_view(request, question_uuid=str(uuid1())):
    '''
    This view will get a question based upon the uuid, the request was from a
    search it will return the html of the question for the search result
    page, if it was called to display a single question detail it will return
    the html the question_detail_page expects

    :param request:
    :return:
    '''
    try:
        search_data = get_post_data(request)
        response = prepare_question_search_html(question_uuid)
        return Response({'html': response}, status=200)
    except:
        print 'fail'
        return []
