from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sb_registration.utils import (verify_completed_registration, upload_image)

from .forms import ImageForm

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def upload_image_api(request):
    picture_form = ImageForm(request.FILES or None)
    if request.method == 'POST':
        if picture_form.is_valid():
            print request.FILES
            print request.DATA