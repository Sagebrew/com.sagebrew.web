from uuid import uuid1
from django.conf import settings
from django.shortcuts import render
from django.template import Context
from django.core.urlresolvers import reverse
from django.template.loader import get_template

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import (api_view, permission_classes)

from api.utils import spawn_task
from sb_stats.tasks import update_view_count_task
from sb_docstore.tasks import build_question_page_task
from sb_docstore.utils import get_question_doc
from sb_registration.utils import verify_completed_registration
from .utils import (get_question_by_most_recent, get_question_by_uuid,
                    get_question_by_least_recent, prepare_question_search_html,
                    get_question_by_recent_edit)
from .tasks import (create_question_task)
from .forms import (SaveQuestionForm, GetQuestionForm)


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
    question_data = request.data
    if isinstance(question_data, dict) is False:
        return Response({"please pass a valid JSON Object"}, status=400)
    question_form = GetQuestionForm(question_data)
    if question_form.is_valid() is True:
        html_array = []
        # TODO Can we generalize this so that we don't need the ifs?
        # TODO Can we also make the form a choice form that only allows
        # the available search types as acceptable values?
        if question_data['sort_by'] == 'most_recent':
            response = get_question_by_most_recent()
            if isinstance(response, Exception):
                # TODO Might want to handle this differently
                return Response(status=500)
            for question in response:
                html_array.append(
                    question.render_question_page(request.user.username))
            return Response(html_array, status=200)

        elif question_data['sort_by'] == 'uuid':
            task_data = {"object_uuid": question_data['question_uuid'],
                         "object_type": dict(settings.KNOWN_TYPES)[
                             "0274a216-644f-11e4-9ad9-080027242395"]}
            spawn_task(update_view_count_task, task_data)
            res = get_question_doc(question_data['question_uuid'],
                                   'public_questions', 'public_solutions',
                                   request.user.username)
            if res == {}:
                question_by_uuid = get_question_by_uuid(
                    question_data['question_uuid'], request.user.email)
                task_data = {
                    'question_uuid': question_data['question_uuid'],
                    'question_table': 'public_questions',
                    'solution_table': 'public_solutions'
                }
                spawn_task(build_question_page_task, task_param=task_data)
                if isinstance(question_by_uuid, Exception):
                    # TODO ensure we have pages that will render certain things
                    # for server error and does not exist errors for questions
                    # TODO do we have tests for the above?
                    # TODO Might want to handle this differently
                    return Response(status=500)
                elif question_by_uuid is False:
                    # TODO Might want to handle this differently
                    return Response({"detail": "question does not exist"},
                                    status=400)
                else:
                    return Response(question_by_uuid, status=200)
            else:
                for solution in res['solutions']:
                    spawn_task(update_view_count_task,
                               {'object_uuid': solution['object_uuid'],
                                'object_type': dict(settings.KNOWN_TYPES)[
                                    solution['object_type']]})
                res['solution_count'] = len(res['solutions'])
                t = get_template("question.html")
                c = Context(res)
                return Response(t.render(c), status=200)

        elif question_data['sort_by'] == 'least_recent':
            response = get_question_by_least_recent()
            if isinstance(response, Exception):
                return Response(status=500)
            # is there any potential for get_question_by_least_recent to be
            # None?
            for question in response:
                html_array.append(
                    question.render_question_page(request.user.username))
            # TODO if question is empty we should be returning a 404
            return Response(html_array, status=200)
        # TODO if cannot perform the above TODOs need to at least add
        # an additional else or remove the bottom else specifier and just
        # return the Response anytime it reaches that area
        elif question_data['sort_by'] == 'recent_edit':
            response = get_question_by_recent_edit()
            if isinstance(response, Exception):
                return Response(status=500)
            for question in response:
                html_array.append(
                    question.render_question_page(request.user.username))
            return Response(html_array, 200)
    return Response({"detail": "fail"}, status=400)


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
    response = prepare_question_search_html(question_uuid)
    if response is None:
        return Response(status=500)
    elif response is False:
        return Response(status=404)
    return Response({'html': response}, status=200)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def edit_question_view(request, question_uuid):
    res = get_question_doc(question_uuid, 'public_questions',
                     'public_solutions')
    template_dict = {"title": res['title'],
                     "content": res['content'],
                     "edit": True,
                     "object_uuid": res['object_uuid'],
                     "object_type": res['object_type'],
                     "created": unicode(res['created'])}
    return render(request, 'save_question.html', template_dict)