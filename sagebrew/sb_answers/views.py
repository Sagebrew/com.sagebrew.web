import logging
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from .forms import (SaveAnswerForm)
from .tasks import (save_answer_task)
from api.utils import spawn_task

logger = logging.getLogger('loggly_logs')


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
        return Response({'detail': 'Please provide a valid JSON object'}, status=400)
    #answer_data['content'] = language_filter(answer_data['content'])

    answer_form = SaveAnswerForm(answer_data)
    if answer_form.is_valid():
        spawn_task(task_func=save_answer_task, task_param=answer_form.cleaned_data)
        return Response({'detail': 'successfully posted an answer'}, status=200)
    else:
        return Response({'detail': 'failed to post an answer'}, status=400)
