import pytz
from datetime import datetime, timedelta, date

from django.conf import settings
from django.contrib.auth.models import User

from boto import connect_s3
from boto.s3.key import Key
from neo4j.v1 import CypherError
from neomodel import DoesNotExist

from sagebrew.api.utils import spawn_task
from sagebrew.plebs.tasks import create_wall_task, generate_oauth_info
from sagebrew.plebs.neo_models import Pleb
from sagebrew.sb_base.decorators import apply_defense


def calc_age(birthday):
    """
    This function just calculates and returns the age of a person based on
    given date.

    :param birthday:
    :return:
    """
    today = date.today()
    try:
        return today.year - birthday.year - \
            ((today.month, today.day) < (birthday.month - birthday.day))
    except AttributeError:
        return 0


@apply_defense
def upload_image(folder_name, file_uuid, image_file, type_known=False):
    """
    Creates a connection to the s3 service then uploads the file which was
    passed
    to this function an uses the uuid as the filename.

    :param type_known:
    :param image_file:
    :param folder_name:
    :param file_uuid:
    :return:
    """
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))
    if type_known:
        key_string = "%s/%s" % (folder_name, file_uuid)
        k.content_type = 'image/%s' % file_uuid[file_uuid.find('.') + 1:]
    else:
        key_string = "%s/%s%s" % (folder_name, file_uuid, ".png")
        k.content_type = 'image/png'
    k.key = key_string

    if not isinstance(image_file, str):
        image_file.seek(0)
        k.set_contents_from_string(image_file.read())
    else:
        k.set_contents_from_string(image_file)
    k.make_public()
    image_uri = k.generate_url(expires_in=0, query_auth=False)
    return image_uri


@apply_defense
def delete_image(file_url):
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    b = conn.get_bucket(bucket)
    k = Key(b)
    k.key = file_url
    b.delete_key(k)
    return True


def generate_profile_pic_url(image_uuid):
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))
    key_string = "%s/%s.%s" % (settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                               image_uuid, "png")
    k.key = key_string
    image_uri = k.generate_url(expires_in=0, query_auth=False)
    return image_uri


def create_user_util_test(email, first_name="test", last_name="test",
                          password="test_test", birthday=None, task=False):
    from sagebrew.plebs.serializers import generate_username
    """
    For test purposes only
    :param task:
    :return:
    :param first_name:
    :param last_name:
    :param email:
    :param password:
    :param birthday:
    :return:
    """
    if birthday is None:
        birthday = datetime.now(pytz.utc) - timedelta(days=18 * 365)
    try:
        user = User.objects.get(email=email)
        username = user.username
    except User.DoesNotExist:
        username = generate_username(first_name, last_name)
        user = User.objects.create_user(first_name=first_name,
                                        last_name=last_name,
                                        email=email, password=password,
                                        username=username)
        user.save()
    try:
        pleb = Pleb.get(username=user.username, cache_buster=True)
    except (Pleb.DoesNotExist, DoesNotExist):
        try:
            pleb = Pleb(email=user.email, first_name=user.first_name,
                        last_name=user.last_name, username=user.username,
                        date_of_birth=birthday)
            pleb.save()
        except(CypherError, IOError):
            return False
    except(CypherError, IOError):
        raise False
    if task:
        res = spawn_task(task_func=create_wall_task,
                         task_param={"username": user.username})
        spawn_task(task_func=generate_oauth_info,
                   task_param={'username': user.username,
                               'password': password},
                   countdown=20)
        if isinstance(res, Exception) is True:
            return res
        else:
            return {"task_id": res, "username": username, "user": user,
                    "pleb": pleb}
    return pleb
