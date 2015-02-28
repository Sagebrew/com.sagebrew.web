import pytz
import logging
from uuid import uuid1
from datetime import datetime
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response

from api.utils import (spawn_task)
from sb_docstore.utils import get_wall_docs
from sb_docstore.tasks import build_wall_task
from .tasks import save_post_task
from .utils import (get_pleb_posts)
from .forms import (SavePostForm, GetPostForm)

logger = logging.getLogger('loggly_logs')

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_post_view(request):
    '''
    Creates the post, connects it to the Pleb which posted it

    :param request:
    :return:
    '''
    post_data = request.DATA
    if type(post_data) != dict:
        return Response({"details": "Please Provide a JSON Object"}, status=400)
    try:
        post_form = SavePostForm(post_data)
        valid_form = post_form.is_valid()
    except AttributeError:
        return Response({"details": "Invalid Form"}, status=400)
    if valid_form:
        #post_data['content'] = language_filter(post_data['content'])
        post_form.cleaned_data['post_uuid'] = str(uuid1())
        spawned = spawn_task(task_func=save_post_task,
                             task_param=post_form.cleaned_data)
        if isinstance(spawned, Exception):
            return Response({"detail": "Failed to create post"},
                            status=500)
        post_data = {
            "object_uuid": post_form.cleaned_data['post_uuid'],
            "parent_object": request.user.username,
            "datetime": datetime.now(pytz.utc),
            "last_edited_on": datetime.now(pytz.utc),
            "post_owner": request.user.first_name + " " +
                          request.user.last_name,
            "upvote_number": 0,
            "downvote_number": 0,
            "content": post_form.cleaned_data['content']
        }
        html = render_to_string('post.html', post_data)
        print html
        return Response(
            {"action": "filtered", "filtered_content": post_data,
             "html": html},
            status=200)
    else:
        return Response(post_form.errors, status=400)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_user_posts(request):
    '''
    This view gets all of the posts attached to a user's wall.

    :param request:
    :return:
    '''
    html_array = []
    try:
        post_form = GetPostForm(request.DATA)
        valid_form = post_form.is_valid()
    except AttributeError:
        return Response(status=404)
    if valid_form:
        posts = get_wall_docs(request.user.username)
        if not posts:
            posts = get_pleb_posts(request.user.email,
                                   post_form.cleaned_data['range_end'],
                                   post_form.cleaned_data['range_start'])
            for post in posts:
                html_array.append(post.render_post_wall_html(
                    post_form.cleaned_data['current_user']))
            task_dict = {'username': request.user.username}
            spawn_task(task_func=build_wall_task, task_param=task_dict)
        else:
            for post in posts:
                post_dict = dict(post)
                post_dict['user'] = request.user
                post_dict['last_edited_on'] = \
                    datetime.strptime(post_dict['last_edited_on'][
                                      :len(post_dict['last_edited_on'])-6],
                                      '%Y-%m-%d %H:%M:%S.%f')
                # TODO replace with actual vote count. Note that the template
                # tag operations require it to be a string and not an int.
                # The tag values also don't accomodate for dynamic updates
                # from javascript so we'll have to figure that out that as well
                # Example when someone transitions from 9 to 10 and 99 to 100
                post_dict['object_vote_count'] = "10k"
                post_dict['vote_type'] = "true"
                post_dict['current_pleb'] = request.user
                html = render_to_string('post.html', post_dict)
                html_array.append(html)

        return Response({'html': html_array}, status=200)
    else:
        return Response(status=400)