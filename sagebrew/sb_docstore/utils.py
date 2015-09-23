import os
from logging import getLogger

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.exceptions import (JSONResponseError, ItemNotFound,
                                       ConditionalCheckFailedException,
                                       ValidationException,
                                       ResourceNotFoundException,
                                       ProvisionedThroughputExceededException)

from django.conf import settings

from sb_base.decorators import apply_defense

logger = getLogger('loggly_logs')


def get_table_name(name):
    branch = os.environ.get("CIRCLE_BRANCH", "unknown").replace('/', '-')
    if branch in name:
        return name
    return "%s-%s" % (branch, name)


def connect_to_dynamo():
    """
    This function gets the connection to dynamodb.

    The only possibly exception it will throw is IOError and there is not
    a lot we can do to handle it because dynamo has scaling retry times
    and in the case that dynamo goes down we will have bigger things to worry
    about. This is currently not an issue. We discussed serving pages
    directly from neo in the case that dynamo is down but because we currently
    use AWS for a lot of our services, if dynamo is down AWS will most likely
    be down. Also there will be three instances of dynamo on our AWS cloud.

    :return:
    """
    if settings.DYNAMO_IP is None:
        conn = DynamoDBConnection(
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        )
    else:
        conn = DynamoDBConnection(
            host=settings.DYNAMO_IP,
            port=8000,
            aws_secret_access_key='anything',
            is_secure=False,
        )
    return conn


def add_object_to_table(table_name, object_data):
    """
    This function will attempt to add an object to a table, this will be
    used to build each table and build the docstore. This is a generalized
    function and will work for every table
    :param table_name:
    :param object_data:
    :return:
    """
    table_name = get_table_name(table_name)
    conn = connect_to_dynamo()
    try:
        table_name = get_table_name(table_name)
        table = Table(table_name=table_name, connection=conn)
    except (JSONResponseError, ResourceNotFoundException) as e:
        raise e
    try:
        table.put_item(data=object_data)
    except ConditionalCheckFailedException:
        try:
            table.get_item(username=object_data['username'])
            return True
        except (ConditionalCheckFailedException, KeyError):
            return True
    except (ValidationException, JSONResponseError) as e:
        # TODO if we receive these errors we probably want to do
        # something other than just return e. Don't they mean the
        # table doesn't exist?
        raise e

    return True


def update_vote(object_uuid, user, vote_type, time):
    conn = connect_to_dynamo()
    try:
        votes_table = Table(table_name=get_table_name('votes'),
                            connection=conn)
    except JSONResponseError as e:
        raise e
    try:
        vote = votes_table.get_item(
            parent_object=object_uuid,
            user=user
        )
    except(ItemNotFound, ProvisionedThroughputExceededException) as e:
        raise e
    previous = vote['status']
    if vote['status'] == vote_type:
        vote['status'] = 2
    else:
        vote['status'] = vote_type
    vote['time'] = time
    vote.partial_save()
    return vote, previous


def get_vote_count(object_uuid, vote_type):
    conn = connect_to_dynamo()
    votes_table = Table(table_name=get_table_name('votes'), connection=conn)

    votes = votes_table.query_2(parent_object__eq=object_uuid,
                                status__eq=vote_type,
                                index="VoteStatusIndex")
    return len(list(votes))


def get_user_updates(username, object_uuid, table_name):
    conn = connect_to_dynamo()
    try:
        table = Table(table_name=get_table_name(table_name), connection=conn)
    except JSONResponseError as e:
        logger.exception("Table %s returned JSONResponse Error" % table_name)
        raise e
    try:
        res = table.get_item(
            parent_object=object_uuid,
            user=username
        )
    except ItemNotFound:
        return {}
    return dict(res)


def get_vote(object_uuid, user):
    conn = connect_to_dynamo()
    votes_table = Table(table_name=get_table_name('votes'), connection=conn)
    try:
        vote = votes_table.get_item(
            parent_object=object_uuid,
            user=user
        )
        return vote
    except (ItemNotFound, JSONResponseError, ValidationException):
        return None
