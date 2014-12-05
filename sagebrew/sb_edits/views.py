import logging
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import EditObjectForm, EditQuestionForm
from .tasks import edit_object_task, edit_question_task

from api.utils import spawn_task
from api.tasks import get_pleb_task
from sb_docstore.tasks import add_object_to_table_task

logger = logging.getLogger('loggly_logs')


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def edit_object_view(request):
    try:
        edit_object_form = EditObjectForm(request.DATA)
        valid_form = edit_object_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        choice_dict = dict(settings.KNOWN_TYPES)
        task_data = {
            "object_type": choice_dict[
                edit_object_form.cleaned_data['object_type']],
            "object_uuid": edit_object_form.cleaned_data['object_uuid'],
            "content": edit_object_form.cleaned_data['content']
        }
        pleb_data = {
            'email': request.user.email,
            'task_func': edit_object_task,
            'task_param': task_data
        }
        spawned = spawn_task(task_func=get_pleb_task, task_param=pleb_data)
        if isinstance(spawned, Exception):
            return Response({"detail": "server error"}, status=500)
        return Response({"detail": "success"}, status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)



@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def edit_question_title_view(request):
    try:
        edit_question_form = EditQuestionForm(request.DATA)
        valid_form = edit_question_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        choice_dict = dict(settings.KNOWN_TYPES)
        task_data = {
            "object_type": choice_dict[
                edit_question_form.cleaned_data['object_type']],
            "object_uuid": edit_question_form.cleaned_data['object_uuid'],
            "question_title": edit_question_form.cleaned_data['question_title']
        }
        pleb_data = {
            'email': request.user.email,
            'task_func': edit_question_task,
            'task_param': task_data
        }
        spawned = spawn_task(task_func=get_pleb_task, task_param=pleb_data)
        if isinstance(spawned, Exception):
            return Response({"detail": "invalid form"}, status=500)

        return Response({"detail": "success"}, status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)
