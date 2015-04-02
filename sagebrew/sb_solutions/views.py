import markdown
import pytz
from uuid import uuid1
from datetime import datetime

from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.reverse import reverse

from django.contrib.auth.decorators import login_required, user_passes_test

from api.utils import spawn_task, request_to_api
from sb_docstore.utils import get_solution_doc
from sb_registration.utils import verify_completed_registration

from .forms import (SaveSolutionForm)
from .tasks import (save_solution_task)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_solution_view(request):
    '''
    The api endpoint which takes a dictionary to create an solution to a question

    :param request:

                    dict = {'content': '',
                            'question_uuid': '', 'to_pleb': ''}

    :return:
    '''
    solution_data = request.data
    if type(solution_data) != dict:
        return Response({'detail': 'Please provide a valid JSON object'},
                        status=400)
    solution_form = SaveSolutionForm(solution_data)
    if solution_form.is_valid():
        solution_form.cleaned_data['solution_uuid'] = str(uuid1())
        solution_form.cleaned_data["current_pleb"] = request.user.username
        spawned = spawn_task(task_func=save_solution_task,
                             task_param=solution_form.cleaned_data)
        if isinstance(spawned, Exception) is True:
            return Response({'detail': 'failed to post an solution'},
                            status=500)
        created_at = datetime.now(pytz.utc)
        user_url = reverse('user-detail', kwargs={
            'username': request.user.username}, request=request)
        user_url = "%s%s" % (user_url, "?expand=True")
        response = request_to_api(user_url, request.user.username,
                                  req_method="GET")
        response_json = response.json()
        profile_data = response_json["profile"]
        response_json.pop("profile", None)
        solution = {
            "solution": {
                "object_uuid": solution_form.cleaned_data['solution_uuid'],
                "upvotes": '0',
                "downvotes": '0',
                "vote_count": '0',
                "vote_type": None,
                "content": solution_form.cleaned_data['content'],
                "html_content": markdown.markdown(
                    solution_form.cleaned_data['content']),
                "parent_object": solution_form.cleaned_data['question_uuid'],
                "last_edited_on": created_at,
                "owner": request.user.username,
                "owner_full_name": request.user.get_full_name(),
                "created": created_at,
                "comments": [],
                "edits": [],
                'object_type': "02241aee-644f-11e4-9ad9-080027242395",
                "profile": profile_data,
                "owner_object": response_json
            },
            "current_user_username": request.user.username
        }

        return Response({'detail': 'successfully posted an solution',
                         'html': render_to_string('solution.html', solution)},
                        status=200)
    else:
        return Response({'detail': 'failed to post an solution'}, status=400)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def edit_solution_view(request, question_uuid, solution_uuid):
    res = get_solution_doc(question_uuid, solution_uuid)
    if isinstance(res, Exception):
        return redirect("404_Error")
    return render(request, 'edit_solution.html', res)

