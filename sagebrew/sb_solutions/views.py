import markdown
from uuid import uuid1
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.generics import ListAPIView

from api.utils import spawn_task

from .forms import (SaveSolutionForm)
from .tasks import (save_solution_task)
from .serializers import SolutionSerializer
from .dynamo_table import SolutionModel




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
                "up_vote_number": 0,
                "down_vote_number": 0,
                "object_vote_count": str(0),
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


class QuestionSolutionList(ListAPIView):
    serializer_class = SolutionSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "parent_object"
    lookup_url_kwarg = "uuid"

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        queryset = SolutionModel.query(parent_object=self.kwargs[
            self.lookup_url_kwarg])
        created = self.request.QUERY_PARAMS.get('created', None)
        if created is not None:
            queryset = sorted(queryset, key=lambda k: k['time_created'])
        modified = self.request.QUERY_PARAMS.get('modified', None)
        if modified is not None:
            queryset = sorted(queryset, key=lambda k: k['last_edited_on'])
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(owner=self.request.user)