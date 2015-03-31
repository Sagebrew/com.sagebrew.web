import pytz
import logging
from uuid import uuid1
from datetime import datetime

from django.template.loader import render_to_string
from django.template import RequestContext
from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from neomodel.exception import CypherException

from api.utils import (spawn_task, request_to_api)
from sb_docstore.utils import get_wall_docs
from sb_docstore.tasks import build_wall_task
from sb_stats.tasks import update_view_count_task
from plebs.neo_models import Pleb

from .tasks import save_post_task
from .utils import (get_page_user_posts)
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
    created_preunicode = datetime.now(pytz.utc)
    post_data = request.data
    try:
        pleb = Pleb.nodes.get(username=request.user.username)
    except(CypherException, IOError) as e:
        return Response({"details": "Server Error"}, status=500)
    if type(post_data) != dict:
        return Response({"details": "Please Provide a JSON Object"}, status=400)

    post_form = SavePostForm(post_data)
    if post_form.is_valid():
        post_form.cleaned_data['post_uuid'] = str(uuid1())
        post_form.cleaned_data['created'] = created_preunicode
        html_content = post_form.cleaned_data['content']
        spawned = spawn_task(task_func=save_post_task,
                             task_param=post_form.cleaned_data)
        if isinstance(spawned, Exception):
            return Response({"detail": "Failed to create post"},
                            status=500)
        post_data = {
            "profile_pic": pleb.profile_pic,
            'object_type': "01bb301a-644f-11e4-9ad9-080027242395",
            "object_uuid": post_form.cleaned_data['post_uuid'],
            "created": unicode(created_preunicode),
            "last_edited_on": datetime.now(pytz.utc),
            "post_owner_full_name": request.user.get_full_name(),
            "post_owner_username": request.user.username,
            "upvotes": 0,
            "downvotes": 0,
            "content": post_form.cleaned_data['content'],
            "vote_count": "0",
            "vote_type": None,
            "html_content": html_content,
            "user": {"username": request.user.username},
        }
        c = RequestContext(request, post_data)
        html = render_to_string('post.html', post_data, context_instance=c)

        return Response({
            "action": "filtered", "filtered_content": post_data,
            "html": html}, status=200)
    else:
        return Response(post_form.errors, status=400)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_page_posts(request):
    '''
    This view gets all of the posts attached to a user's wall.

    :param request:
    :return:
    '''
    html_array = []
    post_form = GetPostForm(request.data)

    if post_form.is_valid():
        posts = get_wall_docs(
            post_form.cleaned_data['page_user'],
            request.user.username)
        if posts is False:
            posts = get_page_user_posts(post_form.cleaned_data['page_user'],
                                        post_form.cleaned_data['range_end'],
                                        post_form.cleaned_data['range_start'])
            for post in posts:
                html_array.append(post.render_post_wall_html(request.user))
                task_data = {
                    "object_type": dict(settings.KNOWN_TYPES)[post.object_type],
                    "object_uuid": post.object_uuid,
                }
                spawn_task(update_view_count_task, task_data)
            task_dict = {'username': post_form.cleaned_data['page_user']}
            spawn_task(task_func=build_wall_task, task_param=task_dict)
            # TODO Shouldn't we return something here other than a 400? We
            # should be able to populate based on Neo
        else:
            for post in posts:
                try:
                    post["current_user"] = request.user.username
                    user_url = reverse(
                        'profile-detail', kwargs={
                            'username': post['post_owner_username']},
                        request=request)
                    response = request_to_api(user_url, request.user.username,
                                              req_method="GET")
                    post_owner = response.json()
                    post['profile_pic'] = post_owner["profile_pic"]
                    post['last_edited_on'] = datetime.strptime(
                        post['last_edited_on'][:len(
                            post['last_edited_on']) - 6],
                        '%Y-%m-%d %H:%M:%S.%f')
                    post['vote_count'] = str(
                        post['upvotes'] - post['downvotes'])
                    task_data = {
                        "object_type": dict(
                            settings.KNOWN_TYPES)[post['object_type']],
                        'object_uuid': post['object_uuid']
                    }
                    spawn_task(update_view_count_task, task_data)
                    for item in post["comments"]:
                        item['last_edited_on'] = datetime.strptime(
                            item['last_edited_on'][:len(
                                item['last_edited_on']) - 6],
                            '%Y-%m-%d %H:%M:%S.%f')
                        item['vote_count'] = str(
                            item['upvotes'] - item['downvotes'])
                    c = RequestContext(request, post)
                    html = render_to_string('post.html', post,
                                            context_instance=c)
                    html_array.append(html)
                except KeyError as e:
                    print e.message
                    continue
        return Response({'html': html_array}, status=200)
    else:
        return Response(status=400)