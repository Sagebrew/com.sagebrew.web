import logging
import pytz
from datetime import datetime
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import EditObjectForm, EditQuestionForm
from .tasks import edit_object_task, edit_question_task

from api.utils import spawn_task
from api.tasks import get_pleb_task
from sb_docstore.utils import add_object_to_table, update_doc, get_table_name
from sb_docstore.tasks import add_object_to_table_task

logger = logging.getLogger('loggly_logs')


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def edit_object_view(request):
    print request.DATA
    try:
        edit_object_form = EditObjectForm(request.DATA)
        valid_form = edit_object_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        current_datetime = unicode(datetime.now(pytz.utc))
        choice_dict = dict(settings.KNOWN_TYPES)
        dynamo_data = {
                'parent_object': edit_object_form.cleaned_data['object_uuid'],
                'datetime': current_datetime,
                'content': edit_object_form.cleaned_data['content'],
                'user': request.user.email,
                'object_type':
                    choice_dict[edit_object_form.cleaned_data['object_type']]
            }
        updates = [
            {'update_key': 'content',
             'update_value': edit_object_form.cleaned_data['content']},
            {'update_key': 'last_edited_on',
             'update_value': current_datetime}
        ]
        table = settings.KNOWN_TABLES[
                             edit_object_form.cleaned_data['object_type']]
        print table
        if table == 'posts' or table=='comments':
            obj_datetime = unicode(edit_object_form.cleaned_data['datetime'])
            parent_object = edit_object_form.cleaned_data['parent_object']
        else:
            obj_datetime = ""
            parent_object = edit_object_form.cleaned_data['parent_object']
        print obj_datetime, parent_object
        res = update_doc(table,
                         edit_object_form.cleaned_data['object_uuid'],
                         updates,
                         parent_object,
                         obj_datetime)
        if isinstance(res, Exception) is True:
            return Response({"detail": "server error"}, status=500)
        res = add_object_to_table('edits', dynamo_data)
        if isinstance(res, Exception) is True:
            return Response({"detail": "server error"}, status=500)
        html_string = "%s%s" % ("#sb_content_",
                                edit_object_form.cleaned_data['object_uuid'])
        return Response({"detail": "success",
                         "content": edit_object_form.cleaned_data['content'],
                         "html_object": html_string},
                        status=200)
    else:
        print edit_object_form.errors
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
            return Response({"detail": "server error"}, status=500)
        dynamo_data = {
            'table': 'edits', 'object_data':
            {
                'parent_object': edit_question_form.cleaned_data
                ['object_uuid'],
                'datetime': unicode(datetime.now(pytz.utc)),
                'question_title': edit_question_form.cleaned_data
                ['question_title']
            }
        }
        res = spawn_task(task_func=add_object_to_table_task,
                         task_param=dynamo_data)
        if isinstance(res, Exception):
            return Response({'detail': 'server error'}, status=500)

        return Response({"detail": "success"}, status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)
