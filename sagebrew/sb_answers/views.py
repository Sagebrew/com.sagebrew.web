from uuid import uuid1
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from .forms import (SaveAnswerForm)
from .tasks import (save_answer_task)
from api.utils import spawn_task



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_answer_view(request):
    '''
    The api endpoint which takes a dictionary to create an answer to a question

    :param request:

                    dict = {'content': '', 'current_pleb': '',
                            'question_uuid': '', 'to_pleb': ''}

    :return:
    '''
    answer_data = request.DATA
    if type(answer_data) != dict:
        return Response({'detail': 'Please provide a valid JSON object'},
                        status=400)
    try:
        answer_data['current_pleb'] = request.user.username
        answer_form = SaveAnswerForm(answer_data)
        valid_form = answer_form.is_valid()
    except AttributeError:
        return Response({'detail': 'failed to post an answer'}, status=400)
    if valid_form:
        answer_form.cleaned_data['answer_uuid'] = str(uuid1())
        spawned = spawn_task(task_func=save_answer_task,
                             task_param=answer_form.cleaned_data)
        if isinstance(spawned, Exception) is True:
            return Response({'detail': 'failed to post an answer'}, status=500)
        solution_data = {
            "answer": {
                "object_uuid": answer_form.cleaned_data['answer_uuid'],
                "up_vote_number": 0,
                "down_vote_number": 0,
                "content": answer_form.cleaned_data['content'],
                "answer_owner_url": request.user.username,
                "parent_object": answer_form.cleaned_data['question_uuid'],
                "owner": request.user.first_name + " " + request.user.last_name
            }
        }
        html = render_to_string('answer_detail.html', solution_data)
        return Response({'detail': 'successfully posted an answer',
                         'html': html}, status=200)
    else:
        return Response({'detail': 'failed to post an answer'}, status=400)
