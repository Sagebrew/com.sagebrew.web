from uuid import uuid1
from django.conf import settings

from _6px import PX
from boto import connect_s3
from boto.s3.key import Key


def get_image_s3(uuid):
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))

def resize_image(url, height, width):
    px = PX.init(
        user_id=settings.PX_USER_ID,
        api_key=settings.PX_API_KEY,
        api_secret=settings.PX_SECRET_KEY
    )
    f_uuid = str(uuid1())
    px.load(f_uuid, url)
    out = px.output({f_uuid: "%sx%s"%(height, width)})
    out.resize({"width": width, "height": height})

    out.url(settings.MASKED_NAME)
    res = px.save()
    print res

    print res.get_output(f_uuid)