from uuid import uuid1
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import CypherException

from api.utils import execute_cypher_query, spawn_task
from .forms import (SubmitFriendRequestForm, GetFriendRequestForm,
                    RespondFriendRequestForm)
from .neo_models import FriendRequest
from .tasks import create_friend_request_task
from plebs.neo_models import Pleb


