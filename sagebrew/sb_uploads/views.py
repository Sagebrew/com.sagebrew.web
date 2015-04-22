from uuid import uuid1
from django.conf import settings
from django.template.loader import render_to_string

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sb_registration.utils import (upload_image)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def upload_image_api(request):
    urls = []
    if request.method == 'POST':
        file_data = dict(request.FILES)
        for item in file_data.values():
            uuid = str(uuid1())
            res = upload_image(settings.AWS_UPLOAD_IMAGE_FOLDER_NAME,
                               uuid, item[0])
            urls.append(res)
    html = render_to_string(
        "image_post.html", {
            "urls": urls,
            "parent_object": request.user.username
        })
    return Response(
        {
            "detail": "success",
            "html": html,
            "urls": urls
        }, 200)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_image_api(request):
    return Response('https://sagebrew-dev.s3.amazonaws.com/'
                    'media/590861ae-9e7d-11e4-8474-080027242395.jpg', 200)
