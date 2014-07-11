from uuid import uuid1
from urllib2 import HTTPError
from requests import ConnectionError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.shortcuts import render

from plebs.neo_models import Pleb
from api.utils import get_post_data



@api_view(['POST'])
def create_notification(request):
    pass

@api_view(['POST'])
def get_notifications(request):
    citizen = Pleb.index.get(email = request.DATA['email'])
    notifications = citizen.traverse('notifications').where('seen', '=', False).run()
    return Response(notifications, status=200)






