from operator import itemgetter

from django.conf import settings
from django.shortcuts import render
from elasticsearch import Elasticsearch
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from api.alchemyapi import AlchemyAPI
from api.utils import (spawn_task)
from sb_registration.utils import verify_completed_registration

from .tasks import update_search_query


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def search_result_view(request):
    return render(request, 'search.html')
