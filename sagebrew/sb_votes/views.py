import logging
from json import dumps
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist

from .forms import VoteObjectForm
from .tasks import vote_object_task
from plebs.neo_models import Pleb
from api.utils import spawn_task

logger = logging.getLogger('loggly_logs')


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def vote_object_view(request):
    try:
        vote_object_form = VoteObjectForm(request.DATA)
        if vote_object_form.is_valid():
            try:
                pleb = Pleb.nodes.get(email=vote_object_form.
                                      cleaned_data['current_pleb'])
            except (Pleb.DoesNotExist, DoesNotExist):
                return Response({"detail": "pleb does not exist"}, status=401)
            choice_dict = dict(settings.KNOWN_TYPES)
            task_data = {
                "current_pleb": pleb,
                "object_type": choice_dict[
                    vote_object_form.cleaned_data['object_type']],
                "object_uuid": vote_object_form.cleaned_data['object_uuid'],
                "vote_type": vote_object_form.cleaned_data['vote_type']
            }
            spawn_task(task_func=vote_object_task, task_param=task_data)

            return Response({"detail": "success"}, status=200)
        else:
            return Response({"detail": "invalid form"}, status=400)
    except AttributeError:
        return Response(status=400)
    except Exception:
        logger.exception(dumps({"function": vote_object_view.__name__,
                                "exception": "Unhandled Exception"}))
        return Response(status=400)