import os
from logging import getLogger

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.exceptions import (JSONResponseError, ItemNotFound,
                                       ConditionalCheckFailedException,
                                       ValidationException,
                                       ResourceNotFoundException)

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
    try:
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
    except IOError as e:
        return e


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
    if isinstance(conn, Exception):
        return conn
    try:
        table_name = get_table_name(table_name)
        table = Table(table_name=table_name, connection=conn)
    except (JSONResponseError, ResourceNotFoundException) as e:
        return e
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
        return e

    return True


@apply_defense
def update_vote(object_uuid, user, vote_type, time):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        votes_table = Table(table_name=get_table_name('votes'),
                            connection=conn)
    except JSONResponseError as e:
        return e
    try:
        vote = votes_table.get_item(
            parent_object=object_uuid,
            user=user
        )
    except ItemNotFound as e:
        return e
    if vote['status'] == vote_type:
        vote['status'] = 2
    else:
        vote['status'] = vote_type
    vote['time'] = time
    vote.partial_save()
    return vote


@apply_defense
def get_vote_count(object_uuid, vote_type):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        votes_table = Table(table_name=get_table_name('votes'), connection=conn)
    except JSONResponseError as e:
        return e
    # Handle ProvisionedThroughputExceededException in calling function.
    # We do it that way because we fall back to cypher and the query currently
    # depends on up/down vote in a different way than dynamo handles it. If we
    # where to do it here it would cause the function to become unwieldy and
    # create too large of a scope for the fxn.
    votes = votes_table.query_2(parent_object__eq=object_uuid,
                                status__eq=vote_type,
                                index="VoteStatusIndex")
    return len(list(votes))


@apply_defense
def get_user_updates(username, object_uuid, table_name):
    conn = connect_to_dynamo()
    if isinstance(conn, IOError):
        logger.critical("Could not connect to dynamo")
        raise conn
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


def get_dynamo_table(table_name):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        table = Table(table_name=get_table_name(table_name),
                      connection=conn)
    except JSONResponseError as e:
        return e

    return table


@apply_defense
def get_vote(object_uuid, user):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        # TODO implement fall back on neo
        return conn
    try:
        votes_table = Table(table_name=get_table_name('votes'),
                            connection=conn)
    except JSONResponseError as e:
        # TODO implement fall back on neo
        return e
    try:
        vote = votes_table.get_item(
            parent_object=object_uuid,
            user=user
        )
        return vote
    except (ItemNotFound, JSONResponseError, ValidationException):
        # TODO implement fall back on neo
        return None
