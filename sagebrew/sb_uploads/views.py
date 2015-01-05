from uuid import uuid1
from django.conf import settings
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
    if request.method == 'POST':
        uuid = str(uuid1())
        file_data = dict(request.FILES)
        for item in file_data.values():
            res = upload_image(settings.AWS_UPLOAED_IMAGE_FOLDER_NAME,
                               uuid, item[0])
            print res
    return Response({"detail": "success"}, 200)