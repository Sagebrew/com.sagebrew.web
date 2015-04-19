from datetime import datetime
import boto.ses
from boto.ses.exceptions import SESMaxSendingRateExceededError
from datetime import date
from django.conf import settings
from django.contrib.auth.models import User

from boto import connect_s3
from boto.s3.key import Key
from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from plebs.tasks import create_pleb_task
from plebs.neo_models import Pleb, BetaUser
from sb_base.decorators import apply_defense


def calc_age(birthday):
    '''
    This function just calculates and returns the age of a person based on
    given date.

    :param birthday:
    :return:
    '''
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day)
                                         < (birthday.month - birthday.day))


@apply_defense
def upload_image(folder_name, file_uuid, image_file):
    '''
    Creates a connection to the s3 service then uploads the file which was
    passed
    to this function an uses the uuid as the filename.

    :param folder_name:
    :param file_uuid:
    :return:
    '''
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))
    key_string = "%s/%s.%s" % (folder_name, file_uuid, "png")
    k.key = key_string
    k.set_contents_from_file(image_file)
    k.make_public()
    image_uri = k.generate_url(expires_in=0, query_auth=False)
    return image_uri


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


def verify_completed_registration(user):
    '''
    This function checks if the user has complete registration, it is used
    in the user_passes_test decorator

    :param user:
    :return:
    '''
    try:
        pleb = Pleb.nodes.get(username=user.username)
        return pleb.completed_profile_info
    except (Pleb.DoesNotExist, DoesNotExist, CypherException):
        return False


def verify_verified_email(user):
    '''
    This function checks if the user has verified their email address,
    It is used in the user_passes_test decorator

    :param user:
    :return:
    '''
    try:
        pleb = Pleb.nodes.get(username=user.username)
        return pleb.email_verified
    except (Pleb.DoesNotExist, DoesNotExist):
        return False
    except CypherException as e:
        return e


@apply_defense
def sb_send_email(source, to_email, subject, html_content):
    '''
    This function is used to send mail through the amazon ses service,
    we can use this for any emails we send just specify html content

    :param to_email:
    :param subject:
    :param html_content:
    :return:
    '''
    try:
        conn = boto.ses.connect_to_region(
            'us-east-1',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        conn.send_email(source=source, subject=subject,
                        body=html_content, to_addresses=[to_email],
                        format='html')
        return True
    except SESMaxSendingRateExceededError as e:
        return e


def generate_username(first_name, last_name):
    users_count = User.objects.filter(first_name__iexact=first_name).filter(
        last_name__iexact=last_name).count()
    username = "%s_%s" % (first_name.lower(), last_name.lower())
    if len(username) > 30:
        username = username[:30]
        users_count = User.objects.filter(username__iexact=username).count()
        if users_count > 0:
            username = username[:(30 - len(users_count))] + str(users_count)
    elif len(username) < 30 and users_count == 0:
        username = "%s_%s" % (
            (''.join(e for e in first_name if e.isalnum())).lower(),
            (''.join(e for e in last_name if e.isalnum())).lower())
    else:
        username = "%s_%s%d" % (
            (''.join(e for e in first_name if e.isalnum())).lower(),
            (''.join(e for e in last_name if e.isalnum())).lower(),
            users_count)
    return username


@apply_defense
def create_user_util(first_name, last_name, email, password, birthday):
    username = generate_username(first_name, last_name)
    user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                    email=email, password=password,
                                    username=username)
    user.save()
    try:
        Pleb.nodes.get(username=user.username)
    except (Pleb.DoesNotExist, DoesNotExist):
        try:
            pleb = Pleb(email=user.email,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        username=user.username,
                        birthday=birthday)
            pleb.save()
            try:
                beta_user = BetaUser.nodes.get(email=email)
                pleb.beta_user.connect(beta_user)
            except(BetaUser.DoesNotExist, DoesNotExist):
                pass
            except(CypherException, IOError):
                return False

        except(CypherException, IOError):
            return False
    except(CypherException, IOError):
        raise False
    res = spawn_task(task_func=create_pleb_task,
                     task_param={"user_instance": user, "birthday": birthday,
                                 "password": password})
    if isinstance(res, Exception) is True:
        return res
    else:
        return {"task_id": res, "username": username, "user": user}


def create_user_util_test(email):
    return create_user_util("test", "test", email, "testpassword",
                            datetime.now())
