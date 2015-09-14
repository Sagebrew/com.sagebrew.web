from dateutil import parser

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from neomodel import db

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from api.utils import smart_truncate
from sb_registration.utils import verify_completed_registration
from sb_questions.neo_models import Question

from .serializers import QuestionSerializerNeo
from .utils import prepare_question_search_html, question_html_snapshot


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def submit_question_view_page(request):
    return render(request, 'save_question.html', {})


def question_page(request, sort_by="most_recent"):
    """
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
    """
    tag_array = [{'default': tag, 'display': tag.replace('_', ' ')}
                 for tag in settings.BASE_TAGS]
    if '_escaped_fragment_' in request.GET:
        query = "MATCH (n:Question) WHERE n.to_be_deleted=false RETURN n " \
                "ORDER BY n.created DESC"
        res, _ = db.cypher_query(query)
        queryset = []
        for row in res:
            question = QuestionSerializerNeo(Question.inflate(row[0]),
                                             context={'expand_param': True,
                                                      'request': request}).data
            question['last_edited_on'] = parser.parse(
                question['last_edited_on'])
            queryset.append(question)
        return render(request, 'question_list.html',
                      {"base_tags": tag_array, 'questions': queryset,
                       'html_snapshot': True})
    return render(request, 'question_list.html',
                  {"base_tags": tag_array})


def question_detail_page(request, question_uuid):
    """
    This is the view that displays a single question with all solutions,
    comments,
    references and tags.

    :param request:
    :return:
    """
    question = Question.get(question_uuid)
    description = smart_truncate(question.content, length=150)
    keywords = question.get_tags_string()
    if '_escaped_fragment_' in request.GET:
        return render(request, 'conversation.html', question_html_snapshot(
            request, question, question_uuid, keywords, description))
    return render(request, 'conversation.html', {
        'uuid': question.object_uuid,
        'sort_by': 'uuid',
        'description': description,
        'keywords': keywords,
        'title': question.title
    })


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_question_search_view(request, question_uuid=None):
    """
    This view will get a question based upon the uuid, the request was from a
    search it will return the html of the question for the search result
    page, if it was called to display a single question detail it will return
    the html the question_detail_page expects

    :param request:
    :return:
    """
    if question_uuid is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    response = prepare_question_search_html(question_uuid)
    if response is False:
        return Response(status=404)

    return Response({'html': response}, status=200)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def solution_edit_page(request, solution_uuid=None):
    """
    This view will get a question based upon the uuid, the request was from a
    search it will return the html of the question for the search result
    page, if it was called to display a single question detail it will return
    the html the question_detail_page expects

    :param request:
    :return:
    """
    data = {"object_uuid": solution_uuid}
    return render(request, 'edit_solution.html', data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def question_edit_page(request, question_uuid=None):
    """
    This view will get a question based upon the uuid, the request was from a
    search it will return the html of the question for the search result
    page, if it was called to display a single question detail it will return
    the html the question_detail_page expects

    :param request:
    :return:
    """
    data = {"object_uuid": question_uuid, "edit": True}
    return render(request, 'save_question.html', data)
