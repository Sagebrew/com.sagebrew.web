import logging
from json import dumps
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist

from .forms import EditObjectForm, EditQuestionForm
from .tasks import edit_object_task, edit_question_task
from plebs.neo_models import Pleb
from api.utils import spawn_task

logger = logging.getLogger('loggly_logs')


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def edit_object_view(request):
    try:
        edit_object_form = EditObjectForm(request.DATA)
        if edit_object_form.is_valid():
            try:
                pleb = Pleb.nodes.get(email=edit_object_form.
                                      cleaned_data['current_pleb'])
            except (Pleb.DoesNotExist, DoesNotExist):
                return Response({"detail": "pleb does not exist"}, status=401)
            choice_dict = dict(settings.KNOWN_TYPES)
            task_data = {
                "current_pleb": pleb,
                "object_type": choice_dict[
                    edit_object_form.cleaned_data['object_type']],
                "object_uuid": edit_object_form.cleaned_data['object_uuid'],
                "content": edit_object_form.cleaned_data['content']
            }
            spawn_task(task_func=edit_object_task, task_param=task_data)

            return Response({"detail": "success"}, status=200)
        else:
            return Response({"detail": "invalid form"}, status=400)
    except Exception:
        logger.exception(dumps({"function": edit_object_view.__name__,
                                "exception": "Unhandled Exception"}))
        return Response(status=400)

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def edit_question_title_view(request):
    try:
        edit_question_form = EditQuestionForm(request.DATA)
        if edit_question_form.is_valid():
            try:
                pleb = Pleb.nodes.get(email=edit_question_form.
                                      cleaned_data['current_pleb'])
            except (Pleb.DoesNotExist, DoesNotExist):
                return Response({"detail": "pleb does not exist"}, status=401)
            choice_dict = dict(settings.KNOWN_TYPES)
            task_data = {
                "current_pleb": pleb,
                "object_type": choice_dict[
                    edit_question_form.cleaned_data['object_type']],
                "object_uuid": edit_question_form.cleaned_data['object_uuid'],
                "question_title": edit_question_form.cleaned_data['question_title']
            }
            spawn_task(task_func=edit_question_task, task_param=task_data)

            return Response({"detail": "success"}, status=200)
        else:

            return Response({"detail": "invalid form"}, status=400)
    except Exception:
        logger.exception(dumps({"function": edit_object_view.__name__,
                                "exception": "Unhandled Exception"}))
        return Response(status=400)