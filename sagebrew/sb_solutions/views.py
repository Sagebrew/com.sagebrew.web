import markdown
from uuid import uuid1
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from django.contrib.auth.decorators import login_required, user_passes_test

from api.utils import spawn_task
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

                    dict = {'content': '', 'current_pleb': '',
                            'question_uuid': '', 'to_pleb': ''}

    :return:
    '''
    solution_data = request.DATA
    if type(solution_data) != dict:
        return Response({'detail': 'Please provide a valid JSON object'},
                        status=400)
    try:
        solution_data['current_pleb'] = request.user.username
        solution_form = SaveSolutionForm(solution_data)
        valid_form = solution_form.is_valid()
    except AttributeError:
        return Response({'detail': 'failed to post an solution'}, status=400)
    if valid_form:
        solution_form.cleaned_data['solution_uuid'] = str(uuid1())
        spawned = spawn_task(task_func=save_solution_task,
                             task_param=solution_form.cleaned_data)
        if isinstance(spawned, Exception) is True:
            return Response({'detail': 'failed to post an solution'}, status=500)
        solution_data = {
            "solution": {
                "object_uuid": solution_form.cleaned_data['solution_uuid'],
                "upvotes": 0,
                "downvotes": 0,
                "vote_count": str(0),
                "vote_type": None,
                "content": solution_form.cleaned_data['content'],
                "html_content": markdown.markdown(
                    solution_form.cleaned_data['content']),
                "solution_owner_url": request.user.username,
                "parent_object": solution_form.cleaned_data['question_uuid'],
                "owner": request.user.first_name + " " + request.user.last_name
            }
        }
        html = render_to_string('solution_detail.html', solution_data)
        return Response({'detail': 'successfully posted an solution',
                         'html': html}, status=200)
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

