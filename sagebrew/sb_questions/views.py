from uuid import uuid1

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse

from api.utils import spawn_task
from sb_registration.utils import verify_completed_registration

from .utils import (prepare_question_search_html)
from .tasks import (create_question_task)
from .forms import (SaveQuestionForm)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def submit_question_view_page(request):
    return render(request,'save_question.html',{
        'current_user': request.user.email,
    })


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
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
    return render(request, 'question_list.html',
                  {'email': request.user.email})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def question_detail_page(request, question_uuid=str(uuid1())):
    '''
    This is the view that displays a single question with all solutions, comments,
    references and tags.

    :param request:
    :return:
    '''
    current_user = request.user
    post_data = {'pleb': current_user.email,
                 'sort_by': 'uuid',
                 'uuid': question_uuid}
    #headers = {'content-type': 'application/json'}
    #question = post_to_api(reverse('get_questions'), data=post_data,
    #                       headers=headers)
    return render(request, 'conversation.html', post_data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_question_view(request):
    '''
    This is the API view to create a question

    :param request:

            request.DATA or request.body = {
                'content': '',
                'current_pleb': 'example@email.com'
                'title': ''
            }

    :return:
    '''
    question_data = request.data
    if type(question_data) != dict:
        return Response({"details": "Please provide a valid JSON object"},
                        status=400)
    #question_data['content'] = language_filter(question_data['content'])
    try:
        question_form = SaveQuestionForm(question_data)
        valid_form = question_form.is_valid()
    except AttributeError:
        return Response(status=404)
    if valid_form:
        question_form.cleaned_data['question_uuid'] = str(uuid1())
        question_form.cleaned_data['current_pleb'] = request.user.username
        spawned = spawn_task(task_func=create_question_task,
                             task_param=question_form.cleaned_data)
        if isinstance(spawned, Exception) is True:
            return Response({"detail": "server error"}, status=500)
        url = reverse(question_detail_page, args=[question_form.cleaned_data[
            'question_uuid']])
        return Response({"detail": "filtered",
                         "url": url}
                        , status=200)
    else:
        return Response(question_form.errors, status=400)


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
    response = prepare_question_search_html(question_uuid, request)
    if response is None:
        return Response(status=500)
    elif response is False:
        return Response(status=404)
    return Response({'html': response}, status=200)
