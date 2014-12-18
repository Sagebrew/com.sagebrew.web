from django.conf import settings
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.exceptions import (JSONResponseError, ItemNotFound,
                                       ConditionalCheckFailedException,
                                       ValidationException)

from neomodel import DoesNotExist

from sb_base.decorators import apply_defense
from sb_questions.neo_models import SBQuestion


def connect_to_dynamo():
    '''
    This function gets the connection to dynamodb.

    The only possibly exception it will throw is IOError and there is not
    a lot we can do to handle it because dynamo has scaling retry times
    and in the case that dynamo goes down we will have bigger things to worry
    about. This is currently not an issue. We discussed serving pages
    directly from neo in the case that dynamo is down but because we currently
    use AWS for a lot of our services, if dynamo is down AWS will most likely
    be down. Also there will be three instances of dynamo on our AWS cloud.

    :return:
    '''
    try:
        if settings.DYNAMO_IP is None:
            conn = DynamoDBConnection(
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID
            )
        else:
            conn = DynamoDBConnection(
                host=settings.DYNAMO_IP,
                port=8000,
                aws_secret_access_key='anything',
                is_secure=False
            )
        return conn
    except IOError as e:
        return e

@apply_defense
def add_object_to_table(table_name, object_data):
    '''
    This function will attempt to add an object to a table, this will be
    used to build each table and build the docstore. This is a generalized
    function and will work for every table
    :param table_name:
    :param object_data:
    :return:
    '''
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        table = Table(table_name=table_name, connection=conn)
    except JSONResponseError:
        return False
    try:
        table.put_item(data=object_data)
    except (ConditionalCheckFailedException, ValidationException) as e:
        return e
    return True

@apply_defense
def query_parent_object_table(object_uuid, get_all=False, table_name='edits'):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        edits = Table(table_name=table_name, connection=conn)
    except JSONResponseError as e:
        return e
    res = edits.query_2(
        parent_object__eq=object_uuid,
        datetime__gte='0',
        reverse=True
    )
    if get_all:
        return list(res)
    try:
        return dict(list(res)[0])
    except IndexError:
        return False

@apply_defense
def update_doc(table, object_uuid, update_data, parent_object="", datetime=""):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        db_table = Table(table_name=table, connection=conn)
    except JSONResponseError as e:
        return e
    if datetime != "" and parent_object!="":
        res = db_table.get_item(parent_object=parent_object,
                                datetime=datetime)
    elif parent_object!="":
        res = db_table.get_item(parent_object=parent_object,
                                object_uuid=object_uuid)
    else:
        res = db_table.get_item(object_uuid=object_uuid)

    for item in update_data:
        res[item['update_key']] = item['update_value']
    res.partial_save()
    return res

@apply_defense
def get_question_doc(question_uuid, question_table, solution_table):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    answer_list = []
    try:
        questions = Table(table_name=question_table, connection=conn)
        solutions = Table(table_name=solution_table, connection=conn)
    except JSONResponseError as e:
        return e
    try:
        question = questions.get_item(
            object_uuid=question_uuid
        )
    except ItemNotFound:
        return {}
    answers = solutions.query_2(
        parent_object__eq=question_uuid
    )
    question = dict(question)
    question['up_vote_number'] = get_vote_count(question['object_uuid'],
                                                1)
    question['down_vote_number'] = get_vote_count(question['object_uuid'],
                                                  0)
    for answer in answers:
        answer = dict(answer)
        answer['up_vote_number'] = get_vote_count(answer['object_uuid'],
                                                  1)
        answer['down_vote_number'] = get_vote_count(answer['object_uuid'],
                                                    0)
        answer_list.append(answer)
    question['answers'] = answer_list
    return question

@apply_defense
def build_question_page(question_uuid, question_table, solution_table):
    '''
    This function will build a question page in the docstore,
    it will take the question table and solution table which will be:
    'private_questions'
    'private_solutions'
    'public_questions'
    'public_solutions'
    Then it will build the page into the docstore.
    This includes getting the question object, all the comments associated
    with it and all the solutions associated with it.

    :param question_uuid:
    :param question_table:
    :param solution_table:
    :return:
    '''
    try:
        question = SBQuestion.nodes.get(sb_id=question_uuid)
    except (SBQuestion.DoesNotExist, DoesNotExist) as e:
        return e
    question_dict = question.get_single_dict()
    answer_dicts = question_dict.pop('answers', None)
    add_object_to_table(table_name=question_table, object_data=question_dict)
    for answer in answer_dicts:
        answer['parent_object'] = question_dict['object_uuid']
        add_object_to_table(table_name=solution_table, object_data=answer)
    return True

@apply_defense
def get_vote(object_uuid, user):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        votes_table = Table(table_name='votes', connection=conn)
    except JSONResponseError as e:
        return e
    try:
        vote = votes_table.get_item(
            parent_object=object_uuid,
            user=user
        )
        return vote
    except ItemNotFound:
        return False

@apply_defense
def update_vote(object_uuid, user, vote_type, time):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        votes_table = Table(table_name='votes', connection=conn)
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
        votes_table = Table(table_name='votes', connection=conn)
    except JSONResponseError as e:
        return e
    votes = votes_table.query_2(parent_object__eq=object_uuid,
                                status__eq=vote_type,
                                index="VoteStatusIndex")
    return len(list(votes))

@apply_defense
def get_wall_docs(parent_object):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    post_list = []
    try:
        posts_table = Table(table_name='posts', connection=conn)
        comments_table = Table(table_name='comments', connection=conn)
    except JSONResponseError as e:
        return e
    posts = posts_table.query_2(
        parent_object__eq=parent_object,
        datetime__gte='0',
        reverse=True
    )
    posts = list(posts)
    if len(posts) == 0:
        return False
    for post in posts:
        comment_list = []
        post = dict(post)
        post['up_vote_number'] = get_vote_count(post['object_uuid'], 1)
        post['down_vote_number'] = get_vote_count(post['object_uuid'], 0)
        comments = comments_table.query_2(
            parent_object__eq=post['object_uuid'],
            datetime__gte='0')
        comments = list(comments)
        for comment in comments:
            comment = dict(comment)
            comment['up_vote_number'] = get_vote_count(
                comment['object_uuid'], 1)
            comment['down_vote_number'] = get_vote_count(
                comment['object_uuid'], 0)
            comment_list.append(comment)
        post['comments'] = comment_list
        post_list.append(post)
    return post_list

@apply_defense
def build_wall_docs(pleb):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        post_table = Table(table_name='posts', connection=conn)
        comment_table = Table(table_name='comments', connection=conn)
    except JSONResponseError as e:
        return e
    posts = pleb.wall.all()[0].post.all()
    for post in posts:
        post_data = post.get_single_dict()
        comments = post_data.pop('comments', None)
        post_table.put_item(post_data)
        for comment in comments:
            comment['parent_object'] = post.sb_id
            comment_table.put_item(comment)

    return True

@apply_defense
def get_user_updates(username, object_uuid, table_name):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        table = Table(table_name=table_name, connection=conn)
    except JSONResponseError as e:
        return e
    if table_name=='edits':
        res = table.query_2(
            parent_object__eq=object_uuid,
            user__eq=username,
            index='UserIndex'
        )
    else:
        res = table.get_item(
            parent_object=object_uuid,
            user=username
        )
        return dict(res)
    return list(res)