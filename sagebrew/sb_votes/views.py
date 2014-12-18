import pytz
import logging
from datetime import datetime
from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import VoteObjectForm
from .tasks import vote_object_task
from api.utils import spawn_task
from api.tasks import get_pleb_task
from sb_base.utils import defensive_exception
from sb_docstore.utils import get_vote, add_object_to_table, update_vote

logger = logging.getLogger('loggly_logs')


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def vote_object_view(request):
    now = unicode(datetime.now(pytz.utc))
    try:
        request.DATA['current_pleb'] = request.user.email
        vote_object_form = VoteObjectForm(request.DATA)
        valid_form = vote_object_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        choice_dict = dict(settings.KNOWN_TYPES)
        upvote_value = vote_object_form.cleaned_data['upvote_count']
        downvote_value = vote_object_form.cleaned_data['downvote_count']
        status = int(vote_object_form.cleaned_data['vote_type'])
        vote_data = {
                 "object_type": choice_dict[
                    vote_object_form.cleaned_data['object_type']],
                 "parent_object": vote_object_form.cleaned_data['object_uuid'],
                 "user": request.user.email,
                 "status": status,
                 "time": now
                 }
        res = get_vote(vote_object_form.cleaned_data['object_uuid'],
                       user=request.user.email)
        if isinstance(res, Exception) is True:
            return Response({"detail": "server error"}, status=500)
        if not res:
            add_res = add_object_to_table('votes', vote_data)
            if isinstance(add_res, Exception) is True:
                return Response({"detail": "server error"}, status=500)
            if status == 1:
                upvote_value += 1
            else:
                downvote_value += 1
        else:
            prev_vote = dict(res)
            update = update_vote(vote_object_form.cleaned_data['object_uuid'],
                                 request.user.email,
                                 status, now)
            if isinstance(update, Exception) is True:
                return Response({"detail": "server error"}, status=500)
            prev_status = int(prev_vote['status'])
            update_status = update['status']
            if update_status==2 and prev_status==1:
                upvote_value -= 1
            elif update_status==2 and prev_status==0:
                downvote_value -= 1
            elif update_status==1 and prev_status==0:
                downvote_value -= 1
                upvote_value += 1
            elif update_status==0 and prev_status==1:
                downvote_value += 1
                upvote_value -= 1
            elif update_status==1 and prev_status==2:
                upvote_value += 1
            elif update_status==0 and prev_status==2:
                downvote_value += 1

        version_add = add_object_to_table("vote_versions", vote_data)
        if isinstance(version_add, Exception) is True:
            return Response({"detail": "server error"}, status=500)
        return Response({"detail": "success", "upvote_value": upvote_value,
                         "downvote_value": downvote_value}, status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)
