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
from api.tasks import get_pleb_task
from sb_base.utils import defensive_exception

logger = logging.getLogger('loggly_logs')


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def edit_object_view(request):
    try:
        edit_object_form = EditObjectForm(request.DATA)
        if edit_object_form.is_valid():
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
            spawn_task(task_func=get_pleb_task, task_param=pleb_data)
            return Response({"detail": "success"}, status=200)
        else:
            return Response({"detail": "invalid form"}, status=400)
    except AttributeError:
        return Response(status=400)
    except Exception as e:
        return defensive_exception(edit_object_view.__name__,
                                   e, Response(status=400))

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def edit_question_title_view(request):
    try:
        edit_question_form = EditQuestionForm(request.DATA)
        if edit_question_form.is_valid():
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
            spawn_task(task_func=get_pleb_task, task_param=pleb_data)

            return Response({"detail": "success"}, status=200)
        else:
            return Response({"detail": "invalid form"}, status=400)
    except AttributeError:
        return Response(status=400)
    except Exception as e:
        return defensive_exception(edit_question_title_view.__name__,
                                   e, Response(status=400))