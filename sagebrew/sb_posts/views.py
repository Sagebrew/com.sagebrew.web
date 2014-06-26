from json import loads
from urllib2 import HTTPError
from requests import ConnectionError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.shortcuts import render

from api.utils import get_post_data
from sb_posts.tasks import save_post
from plebs.neo_models import Pleb
from .utils import get_pleb_posts

@api_view(['POST'])
def save_post_view(request):
    '''
    Creates the post, connects it to the Pleb which posted it

    :param request:
    :return:
    '''
    try:
        post_data = get_post_data(request)
        return Response({"detail": "success"}, status=200)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create comment task"},
                            status=408)

@api_view(['POST'])
def get_user_posts(request):
    citizen = Pleb.index.get(email=request.DATA['email'])
    posts = get_pleb_posts(citizen)
    return Response(posts, status=200)