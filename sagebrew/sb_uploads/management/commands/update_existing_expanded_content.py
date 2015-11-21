import requests
import cStringIO
from uuid import uuid1
from mimetypes import guess_extension

from django.conf import settings
from django.core.management.base import BaseCommand

from rest_framework import status

from sb_uploads.neo_models import URLContent
from sb_registration.utils import upload_image


class Command(BaseCommand):
    args = 'None.'

    def update_existing_expanded_content(self):
        for url_object in URLContent.nodes.all():
            if url_object.selected_image:
                try:
                    res = requests.get(url_object.selected_image)
                    if res.status_code == status.HTTP_200_OK:
                        try:
                            temp_file = cStringIO.StringIO(res.content)
                        except IOError:
                            continue
                        if 'image' in res.headers['content-type']:
                            file_ext = guess_extension(
                                res.headers['content-type'])
                        else:
                            file_ext = '.png'

                        image = upload_image(
                            settings.AWS_UPLOAD_IMAGE_FOLDER_NAME,
                            '%s%s' % (str(uuid1()), file_ext),
                            temp_file, True)
                        url_object.selected_image = image
                        url_object.save()
                except (requests.RequestException):
                    continue


    def handle(self, *args, **options):
        self.update_existing_expanded_content()
