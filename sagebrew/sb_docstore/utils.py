import os
from datetime import datetime

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.exceptions import (JSONResponseError, ItemNotFound,
                                       ConditionalCheckFailedException,
                                       ValidationException,
                                       ResourceNotFoundException)

from django.conf import settings

from sb_base.decorators import apply_defense


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


def get_rep_info(parent_object, table_name):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        table = Table(table_name=get_table_name(table_name), connection=conn)
    except JSONResponseError:
        return False

    res = table.query_2(
        parent_object__eq=parent_object,
        object_uuid__gte="a"
    )
    return list(res)


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
        res = table.put_item(data=object_data)
    except ConditionalCheckFailedException:
        try:
            user_object = table.get_item(username=object_data['username'])
            return True
        except (ConditionalCheckFailedException, KeyError):
            return True
    except (ValidationException, JSONResponseError) as e:
        # TODO if we receive these errors we probably want to do
        # something other than just return e. Don't they mean the
        # table doesn't exist?
        return e

    return True


def convert_dynamo_content(raw_content):
    content = dict(raw_content)
    content['upvotes'] = get_vote_count(content['object_uuid'], 1)
    content['downvotes'] = get_vote_count(content['object_uuid'], 0)
    content['last_edited_on'] = datetime.strptime(
        content['last_edited_on'][:len(content['last_edited_on']) - 6],
        '%Y-%m-%d %H:%M:%S.%f')
    content['created'] = datetime.strptime(
        content['created'][:len(content['created']) - 6],
        '%Y-%m-%d %H:%M:%S.%f')
    content['vote_count'] = str(
        content['upvotes'] - content['downvotes'])

    return content


def convert_dynamo_contents(raw_contents):
    content_list = []
    for content in raw_contents:
        converted_content = convert_dynamo_content(content)
        content_list.append(converted_content)
    return content_list


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
    votes = votes_table.query_2(parent_object__eq=object_uuid,
                                status__eq=vote_type,
                                index="VoteStatusIndex")
    return len(list(votes))


@apply_defense
def get_user_updates(username, object_uuid, table_name):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        table = Table(table_name=get_table_name(table_name), connection=conn)
    except JSONResponseError as e:
        return e
    if table_name == 'edits':
        res = table.query_2(
            parent_object__eq=object_uuid,
            user__eq=username,
            index='UserIndex'
        )
    else:
        try:
            res = table.get_item(
                parent_object=object_uuid,
                user=username
            )
        except ItemNotFound:
            return {}
        return dict(res)
    return list(res)


@apply_defense
def build_rep_page(rep):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        rep_table = Table(table_name=get_table_name('general_reps'),
                          connection=conn)
        policy_table = Table(table_name=get_table_name('policies'),
                             connection=conn)
        experience_table = Table(table_name=get_table_name('experiences'),
                                 connection=conn)
    except JSONResponseError as e:
        return e
    policies = rep.policy.all()
    experiences = rep.experience.all()
    try:
        pleb = rep.pleb.all()[0]
    except IndexError as e:
        return e
    rep_data = {
        'object_uuid': str(rep.object_uuid),
        'name': "%s %s" % (pleb.first_name, pleb.last_name),
        'full': '%s %s %s' % (rep.title, pleb.first_name, pleb.last_name),
        'username': pleb.username, 'rep_id': str(rep.object_uuid),
        "bio": str(rep.bio), 'title': rep.title
    }
    rep_table.put_item(rep_data)
    for policy in policies:
        data = {
            'parent_object': rep.object_uuid,
            'object_uuid': policy.object_uuid,
            'category': policy.category,
            'description': policy.description
        }
        policy_table.put_item(data)

    for experience in experiences:
        data = {
            'parent_object': rep.object_uuid,
            'object_uuid': experience.object_uuid,
            'title': experience.title,
            'start_date': unicode(experience.start_date),
            'end_date': unicode(experience.end_date),
            'description': experience.description,
            'current': experience.current,
            'company': experience.company_s,
            'location': experience.location_s
        }
        experience_table.put_item(data)
    return True


@apply_defense
def get_rep_docs(rep_id, rep_only=False):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        rep_table = Table(table_name=get_table_name('general_reps'),
                          connection=conn)
    except JSONResponseError as e:
        return e
    try:
        rep = rep_table.get_item(
            object_uuid=rep_id
        )
    except ItemNotFound:
        return {}
    if rep_only:
        return rep
    policies = get_rep_info(rep_id, 'policies')
    experiences = get_rep_info(rep_id, 'experiences')
    education = get_rep_info(rep_id, 'education')
    goals = get_rep_info(rep_id, 'goals')
    return {"rep": rep, "policies": policies, "experiences": experiences,
            'education': education, 'goals': goals}


@apply_defense
def get_action(username, action):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        action_table = Table(table_name=get_table_name('actions'),
                             connection=conn)
    except JSONResponseError as e:
        return e
    try:
        action_object = action_table.get_item(
            parent_object=username,
            action=action
        )
    except JSONResponseError as e:
        return e
    except ItemNotFound:
        return False
    return dict(action_object)


@apply_defense
def build_privileges(pleb):
    conn = connect_to_dynamo()
    username = pleb.username
    if isinstance(conn, Exception):
        return conn
    try:
        action_table = Table(table_name=get_table_name('actions'),
                             connection=conn)
        privilege_table = Table(table_name=get_table_name('privileges'),
                                connection=conn)
        restriction_table = Table(table_name=get_table_name('restrictions'),
                                  connection=conn)
    except JSONResponseError as e:
        return e

    for privilege in pleb.privileges.all():
        rel = pleb.privileges.relationship(privilege)
        if rel.active:
            privilege_dict = privilege.get_dict()
            privilege_dict['parent_object'] = username
            privilege_table.put_item(privilege_dict, True)

    for action in pleb.actions.all():
        rel = pleb.actions.relationship(action)
        if rel.active:
            for restriction in action.get_restrictions():
                if pleb.restrictions.is_connected(restriction):
                    rel = pleb.restrictions.relationship(restriction)
                    if rel.active:
                        restriction_dict = restriction.get_dict()
                        restriction_dict['parent_object'] = username
                        restriction_table.put_item(restriction, True)
            action_dict = action.get_dict()
            action_dict['parent_object'] = username
            action_table.put_item(action_dict, True)

    for restriction in pleb.restrictions.all():
        rel = pleb.restrictions.relationship(restriction)
        if rel.active:
            rest_dict = restriction.get_dict()
            rest_dict['parent_object'] = username
            restriction.put_item(rest_dict)
    return True


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