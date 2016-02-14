import warnings
import time
import csv
import pytz
import boto.sqs
import requests
import hashlib
import shortuuid
import collections
from uuid import uuid1
from json import dumps
from datetime import datetime
from logging import getLogger

from django.core import signing
from django.conf import settings
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.core.files.temp import NamedTemporaryFile

from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from rest_framework.serializers import ValidationError

from boto.sqs.message import Message

from .alchemyapi import AlchemyAPI

logger = getLogger('loggly_logs')


def request_to_api(url, username, data=None, headers=None, req_method=None,
                   internal=True):
    """
    This function makes a request to the given endpoint. It's a helper function
    that enables us to easily include Sagebrew specific headers if we're hitting
    an internal api but also include headers needed to access an alternative
    API. A full URL must be provided, this is to enable users to include
    external endpoints in Requirements and other API dependent resources.

    :param url:
    :param username:
    :param data:
    :param headers:
    :param req_method:
    :param internal:
    :return:
    """
    # TODO need to remove this as we shouldn't be needing to call a pleb object
    # into api.utils. It has the potential to cause a circular dependency
    if headers is None:
        headers = {"content-type": "application/json"}
    if internal is True and username is not None and username != '':
        token = Token.objects.get(user__username=username)

        headers['Authorization'] = "%s %s" % ('Token', token.key)
    response = None
    try:
        if req_method is None or req_method == "POST" or req_method == "post":
            response = requests.post(url, data=dumps(data),
                                     verify=settings.VERIFY_SECURE,
                                     headers=headers)
        elif req_method == 'get' or req_method == "GET":
            response = requests.get(url, verify=settings.VERIFY_SECURE,
                                    headers=headers)
    except requests.ConnectionError as e:
        logger.exception("ConnectionError ")
        raise e

    return response


def get_oauth_client(username, password, web_address, client_id=None,
                     client_secret=None):
    if client_id is None:
        client_id = settings.OAUTH_CLIENT_ID
    if client_secret is None:
        client_secret = settings.OAUTH_CLIENT_SECRET
    response = requests.post(web_address, data={
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password,
        'grant_type': 'password'}, verify=settings.VERIFY_SECURE)
    return response.json()


def refresh_oauth_access_token(refresh_token, url, client_id=None,
                               client_secret=None):
    if client_id is None:
        client_id = settings.OAUTH_CLIENT_ID
    if client_secret is None:
        client_secret = settings.OAUTH_CLIENT_SECRET
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(url, data=data,
                             verify=settings.VERIFY_SECURE)
    json_response = response.json()
    if "error" in json_response:
        logger.critical("Debugging oauth refresh issue")
        logger.critical(dumps(data))

    return json_response


def check_oauth_needs_refresh(oauth_client):
    elapsed = datetime.now(pytz.utc) - oauth_client.last_modified
    expiration = oauth_client.expires_in - 600
    if elapsed.total_seconds() >= expiration:
        return True
    return False


def get_oauth_access_token(pleb, web_address=None):
    # TODO need to be able to pass creds rather than the username. That way
    # someone can add their creds to the Restriction/Action/etc and use those
    # rather than our internal ones.
    if web_address is None:
        web_address = settings.WEB_ADDRESS + '/o/token/'

    try:
        oauth_creds = [oauth_user for oauth_user in pleb.oauth.all()
                       if oauth_user.web_address == web_address][0]
    except IndexError as e:
        return e
    if check_oauth_needs_refresh(oauth_creds) is True:
        refresh_token = decrypt(oauth_creds.refresh_token)
        updated_creds = refresh_oauth_access_token(refresh_token,
                                                   oauth_creds.web_address)
        oauth_creds.last_modified = datetime.now(pytz.utc)
        try:
            oauth_creds.access_token = encrypt(updated_creds['access_token'])
        except KeyError:
            logger.exception("Access Token issue")
        oauth_creds.token_type = updated_creds['token_type']
        oauth_creds.expires_in = updated_creds['expires_in']
        oauth_creds.refresh_token = encrypt(updated_creds['refresh_token'])
        oauth_creds.save()

    return decrypt(oauth_creds.access_token)


def generate_oauth_user(pleb, password, web_address=None):
    if web_address is None:
        web_address = settings.WEB_ADDRESS + '/o/token/'
    creds = get_oauth_client(pleb.username, password, web_address)

    return creds


def encrypt(data):
    return signing.dumps(data)


def decrypt(data):
    return signing.loads(data)


def generate_short_token():
    short_hash = hashlib.sha1(shortuuid.uuid())
    short_hash.update(settings.SECRET_KEY)
    return short_hash.hexdigest()[::2]


def generate_long_token():
    long_hash = hashlib.sha1(shortuuid.uuid())
    long_hash.update(settings.SECRET_KEY)
    return long_hash.hexdigest()


def add_failure_to_queue(message_info):
    conn = boto.sqs.connect_to_region(
        "us-west-2",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    my_queue = conn.get_queue('sb_failures')
    m = Message()
    m.set_body(dumps(message_info))
    my_queue.write(m)
    return True


def spawn_task(task_func, task_param, countdown=0, task_id=None):
    if task_id is None:
        task_id = str(uuid1())
    try:
        return task_func.apply_async(kwargs=task_param, countdown=countdown,
                                     task_id=task_id)
    except (IOError, Exception) as e:
        failure_uuid = str(uuid1())
        failure_dict = {
            'action': 'failed_task',
            'attempted_task': task_func.__name__,
            'task_info_kwargs': task_param,
            'failure_uuid': failure_uuid
        }
        add_failure_to_queue(failure_dict)
        raise e


def create_auto_tags(content):
    try:
        alchemyapi = AlchemyAPI()
        keywords = alchemyapi.keywords("text", content)
        return keywords
    except Exception as e:
        logger.exception("Auto Tag issue with Alchemy: ")
        return e


def wait_util(async_res):
    while not async_res['task_id'].ready():
        time.sleep(1)
    while not async_res['task_id'].result.ready():
        time.sleep(1)
    return async_res['task_id'].result.result


def gather_request_data(context, expedite_param=None, expand_param=None):
    try:
        request = context['request']
        try:
            expand = request.query_params.get('expand', 'false').lower()
            expedite = request.query_params.get('expedite', "false").lower()
            relations = request.query_params.get(
                'relations', 'primaryKey').lower()
            html = request.query_params.get('html', 'false').lower()
            expand_array = request.query_params.get('expand_attrs', [])
            if html == 'true':
                expand = 'true'
        except AttributeError:
            try:
                expand = request.GET.get('expand', 'false').lower()
                expedite = request.GET.get('expedite', 'false').lower()
                relations = request.GET.get('relations', 'primaryKey').lower()
            except AttributeError:
                expand = 'false'
                expedite = 'false',
                relations = 'primaryKey'
                request = None
            expand_array = []
    except KeyError:
        expand = 'false'
        expedite = 'false'
        relations = "primaryKey"
        request = None
        expand_array = []

    if expedite_param is not None:
        expedite = 'true'
    if expand_param is not None:
        expand = 'true'

    return request, expand, expand_array, relations, expedite


def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    return content[:length].rsplit(' ', 1)[0] + suffix


def flatten_lists(unflattened_list):
    for element in unflattened_list:
        if isinstance(element, collections.Iterable) and not isinstance(
                element, basestring):
            for sub in flatten_lists(element):
                yield sub
        else:
            yield element


def humanize_dict_keys(inhuman_dicts, keys):
    new_keys = []
    for key in keys:
        new_key = key.replace('_', ' ').title()
        [item.update({new_key: item.pop(key, None)}) for item in inhuman_dicts]
        new_keys.append(new_key)
    return inhuman_dicts, new_keys


def generate_csv_html_file_response(name, list_data, keys):
    # use of named temporary file here is to handle deletion of file
    # after we return the file, after the new file object is evicted
    # it gets deleted
    # http://stackoverflow.com/questions/3582414/removing-tmp-file-
    # after-return-httpresponse-in-django
    newfile = NamedTemporaryFile(suffix='.csv', delete=False)
    newfile.name = name
    dict_writer = csv.DictWriter(newfile, keys)
    dict_writer.writeheader()
    dict_writer.writerows(list_data)
    newfile.seek(0)
    wrapper = FileWrapper(newfile)
    httpresponse = HttpResponse(wrapper,
                                content_type="text/csv")
    httpresponse['Content-Disposition'] = 'attachment; filename=%s' \
                                          % newfile.name
    return httpresponse


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


def calc_stripe_application_fee(amount, quest_application_fee,
                                total_donations=1):
    return int(
        (amount *
         (quest_application_fee + settings.STRIPE_TRANSACTION_PERCENT)) +
        (30 * total_donations)
    )


class SBUniqueValidator(UniqueValidator):
    """
    Validator that corresponds to `unique=True` on a model field.

    Should be applied to an individual field on the serializer.
    """

    def filter_queryset(self, value, queryset):
        """
        Filter the queryset to all instances matching the given attribute.
        :param value:
        :param queryset:
        """
        return [x for x in queryset if getattr(x, self.field_name) == value]

    def exclude_current_instance(self, queryset):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict.
        :param queryset:
        """
        if self.instance is not None:
            return [x for x in queryset
                    if x.object_uuid != self.instance.object_uuid]
        return queryset

    def __call__(self, value):
        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset)
        queryset = self.exclude_current_instance(queryset)
        if queryset:
            raise ValidationError(self.message)
