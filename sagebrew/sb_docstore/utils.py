import os
from django.conf import settings
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.exceptions import (JSONResponseError, ItemNotFound,
                                       ConditionalCheckFailedException,
                                       ValidationException)

from neomodel import DoesNotExist, CypherException

from plebs.neo_models import Pleb
from sb_base.decorators import apply_defense
from sb_questions.neo_models import SBQuestion
from sb_reps.neo_models import BaseOfficial
from sb_reps.utils import get_rep_type


def get_table_name(name):
    branch = os.environ.get("CIRCLE_BRANCH", None)
    return "%s-%s" % (branch, name)

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
        table_name = get_table_name(table_name)
        table = Table(table_name=table_name, connection=conn)
    except JSONResponseError as e:
        return e
    try:
        res = table.put_item(data=object_data)
    except ConditionalCheckFailedException:
        try:
            user_object = table.get_item(email=object_data['email'])
            return True
        except ConditionalCheckFailedException as e:
            return True
    except (ValidationException, JSONResponseError) as e:
        # TODO if we receive these errors we probably want to do
        # something other than just return e. Don't they mean the
        # table doesn't exist?
        return e

    return True


@apply_defense
def query_parent_object_table(object_uuid, get_all=False, table_name='edits'):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        edits = Table(table_name=get_table_name(table_name), connection=conn)
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
def update_doc(table, object_uuid, update_data, parent_object="",
               obj_datetime=""):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        db_table = Table(table_name=get_table_name(table), connection=conn)
    except JSONResponseError as e:
        return e
    if obj_datetime != "" and parent_object != "":
        res = db_table.get_item(parent_object=parent_object,
                                datetime=obj_datetime)
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
    q_comments = []
    try:
        questions = Table(table_name=get_table_name(question_table),
                          connection=conn)
        solutions = Table(table_name=get_table_name(solution_table),
                          connection=conn)
        comment_table = Table(table_name=get_table_name("comments"),
                         connection=conn)
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
    comments = comment_table.query_2(
        parent_object__eq=question_uuid,
        datetime__gte="0"
    )
    question = dict(question)
    question['up_vote_number'] = get_vote_count(question['object_uuid'],
                                                1)
    question['down_vote_number'] = get_vote_count(question['object_uuid'],
                                                  0)
    for comment in comments:
        comment = dict(comment)
        print comment
        comment['up_vote_number'] = get_vote_count(comment['object_uuid'],1)
        comment['down_vote_number'] = get_vote_count(comment['object_uuid'],0)
        q_comments.append(comment)
    for answer in answers:
        a_comments = []
        answer = dict(answer)
        answer['up_vote_number'] = get_vote_count(answer['object_uuid'],
                                                  1)
        answer['down_vote_number'] = get_vote_count(answer['object_uuid'],
                                                    0)
        answer_comments = comment_table.query_2(
            parent_object__eq=answer['object_uuid'],
            datetime__gte="0"
        )
        for ans_comment in answer_comments:
            comment = dict(ans_comment)
            comment['up_vote_number'] = get_vote_count(comment['object_uuid'],1)
            comment['down_vote_number'] = get_vote_count(
                comment['object_uuid'],0)
            a_comments.append(comment)
        answer['comments'] = a_comments
        answer_list.append(answer)
    question['answers'] = answer_list
    question['comments'] = q_comments
    print question
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
    add_object_to_table(table_name=get_table_name(question_table),
                        object_data=question_dict)
    for answer in answer_dicts:
        answer['parent_object'] = question_dict['object_uuid']
        add_object_to_table(table_name=get_table_name(solution_table),
                            object_data=answer)
    return True


@apply_defense
def get_vote(object_uuid, user):
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
        return vote
    except ItemNotFound:
        return False


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
def get_wall_docs(parent_object):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    post_list = []
    try:
        posts_table = Table(table_name=get_table_name('posts'),
                            connection=conn)
        comments_table = Table(table_name=get_table_name('comments'),
                               connection=conn)
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


def build_wall_docs(pleb):
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        post_table = Table(table_name=get_table_name('posts'), connection=conn)
        comment_table = Table(table_name=get_table_name('comments'),
                              connection=conn)
    except JSONResponseError as e:
        return e
    try:
        pleb_obj = Pleb.nodes.get(email=pleb)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    try:
        posts = pleb_obj.wall.all()[0].post.all()
    except IndexError as e:
        return e
    for post in posts:
        post_data = post.get_single_dict()
        comments = post_data.pop('comments', None)
        try:
            post_table.put_item(post_data)
        except ConditionalCheckFailedException as e:
            return e
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
        table = Table(table_name=get_table_name(table_name), connection=conn)
    except JSONResponseError as e:
        return e
    if table_name=='edits':
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
def build_rep_page(rep_id, rep_type=None):
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
    if rep_type is None:
        try:
            rep = BaseOfficial.nodes.get(sb_id=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
    else:
        r_type = get_rep_type(dict(settings.BASE_REP_TYPES)[rep_type])
        try:
            rep = r_type.nodes.get(sb_id=rep_id)
        except (r_type.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
    policies = rep.policy.all()
    experiences = rep.experience.all()
    try:
        pleb = rep.pleb.all()[0]
    except IndexError as e:
        return e
    rep_data = {
        'object_uuid': str(rep.sb_id),
        'name': "%s %s"%(pleb.first_name, pleb.last_name),
        'full': '%s %s %s'%(rep.title, pleb.first_name, pleb.last_name),
        'username': pleb.username, 'rep_id': str(rep.sb_id),
        "bio": str(rep.bio), 'title': rep.title
    }
    for key in rep_data.keys():
        print type(rep_data[key])
    rep_table.put_item(rep_data)
    for policy in policies:
        data = {
            'parent_object': rep.sb_id,
            'object_uuid': policy.sb_id,
            'category': policy.category,
            'description': policy.description
        }
        policy_table.put_item(data)

    for experience in experiences:
        data = {
            'parent_object': rep.sb_id,
            'object_uuid': experience.sb_id,
            'title': experience.title,
            'start_date': unicode(experience.start_date),
            'end_date': unicode(experience.end_date),
            'description': experience.description,
            'current': experience.current,
            'company': experience.company_s,
            'location': experience.location_s
        }
        print data
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
def get_notification_docs(username):
    notification_list = []
    conn = connect_to_dynamo()
    if isinstance(conn, Exception):
        return conn
    try:
        notification_table = Table(table_name=get_table_name('notifications'),
                                   connection=conn)
    except JSONResponseError as e:
        return e
    res = notification_table.query_2(
                            parent_object__eq=username,
                            datetime__gte='0')
    for notification in res:
        notification_list.append(dict(notification))
    return notification_list

