from uuid import uuid1
from celery import shared_task

from django.template.loader import render_to_string
from django.core.cache import cache

from rest_framework.reverse import reverse

from neomodel import CypherException, DoesNotExist
from py2neo.cypher.error.statement import ClientError

from api.utils import spawn_task, smart_truncate
from plebs.tasks import update_reputation
from plebs.neo_models import Pleb
from sb_base.neo_models import (get_parent_votable_content,
                                get_parent_titled_content)
from sb_notifications.tasks import spawn_notifications
from sb_comments.neo_models import Comment

from .neo_models import Vote


@shared_task()
def vote_object_task(vote_type, current_pleb, object_uuid):
    """
    This function takes a pleb object, an
    sb_object(Solution, Question, Comment, Post), and a
    vote_type(True, False) it will then call a method to handle the vote
    operations on the sb_object.

    :param vote_type:
    :param current_pleb:
    :param object_uuid:
    :return:
    """
    try:
        current_pleb = Pleb.get(username=current_pleb)
    except (DoesNotExist, Pleb.DoesNotExist, CypherException, IOError) as e:
        raise vote_object_task.retry(exc=e, countdown=10, max_retries=None)
    sb_object = get_parent_votable_content(object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise vote_object_task.retry(exc=sb_object, countdown=10,
                                     max_retries=None)
    query = 'MATCH (v:VotableContent {object_uuid:"%s"}), (p:Pleb {username:"%s"}) WITH v, p OPTIONAL MATCH '
    res = sb_object.vote_content(vote_type, current_pleb)

    if isinstance(res, Exception) is True:
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)

    res = spawn_task(update_reputation, {"username": sb_object.owner_username})

    if isinstance(res, Exception):
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)

    previous_vote_node = sb_object.get_last_user_vote(current_pleb.username)
    previous_vote = 2
    # set previous_vote to 2 here to ensure that a vote notification gets
    # spawned off, previous_vote will change if there is a previous_vote_node
    # but we have this here to make sure that even if there isn't a previous
    # node a notification will get created.
    if previous_vote_node:
        previous_vote = int(previous_vote_node.vote_type)

    res = spawn_task(task_func=object_vote_notifications,
                     task_param={
                         "object_uuid": object_uuid,
                         "previous_vote_type": previous_vote,
                         "new_vote_type": vote_type,
                         "voting_pleb": current_pleb.username
                     })
    if isinstance(res, Exception):
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)
    if previous_vote != vote_type and vote_type != 2:
        res = spawn_task(task_func=create_vote_node,
                         task_param={
                             "node_id": str(uuid1()),
                             "vote_type": vote_type,
                             "voter": current_pleb.username,
                             "parent_object": object_uuid
                         })
        if isinstance(res, Exception):
            raise vote_object_task.retry(exc=res, countdown=10,
                                         max_retries=None)

    return sb_object


@shared_task()
def object_vote_notifications(object_uuid, previous_vote_type, new_vote_type,
                              voting_pleb):
    sb_object = get_parent_votable_content(object_uuid)
    try:
        current_pleb = Pleb.get(username=voting_pleb)
    except (DoesNotExist, Pleb.DoesNotExist, CypherException, ClientError,
            IOError) as e:
        raise object_vote_notifications.retry(exc=e, countdown=10,
                                              max_retries=None)
    if new_vote_type != 2 and previous_vote_type != new_vote_type:
        reputation_change = sb_object.down_vote_adjustment
        modifier = "downvoted"
        reputation_message = ""
        if new_vote_type:
            reputation_change = sb_object.up_vote_adjustment
            modifier = "upvoted"
        if reputation_change:
            # using b tag here because a div or p will break the rendering of
            # the notification html due to them not being allowed in a tags
            color = "sb_reputation_notification_change_red"
            if reputation_change > 0:
                color = "sb_reputation_notification_change_green"
            reputation_message = render_to_string(
                'notification_message.html',
                {'color': color, 'reputation_change':
                    "%+d" % reputation_change})
            if sb_object.visibility != "public":
                reputation_message = ""
        public = False
        action_name = " %s %s %s " % ("%s your" % modifier,
                                      sb_object.get_child_label(),
                                      reputation_message)
        titled_content = get_parent_titled_content(sb_object.object_uuid)
        if not isinstance(titled_content, Exception):
            truncate_content = titled_content.title
        else:
            truncate_content = sb_object.content
        if sb_object.visibility == "public":
            action_name = '%s from vote on "%s"' % (reputation_message,
                                                    smart_truncate(
                                                        truncate_content))
            public = True
        if previous_vote_type != new_vote_type and new_vote_type != 2:
            if sb_object.get_child_label().lower() == "comment":
                comment_on = Comment.get_comment_on(sb_object.object_uuid)
                page_type = comment_on.get_child_label().lower()
                object_id = comment_on.object_uuid
            else:
                page_type = sb_object.get_child_label().lower()
                object_id = sb_object.object_uuid
            res = spawn_task(spawn_notifications, task_param={
                'from_pleb': current_pleb.username,
                'to_plebs': [sb_object.owner_username],
                'sb_object': sb_object.object_uuid,
                'notification_id': str(uuid1()),
                'url': reverse(
                    "single_%s_page" % page_type,
                    kwargs={"object_uuid": object_id}),
                'action_name': action_name,
                'public': public
            })
            if isinstance(res, Exception):
                raise object_vote_notifications.retry(exc=res, countdown=10,
                                                      max_retries=None)
    return True


@shared_task()
def create_vote_node(node_id, vote_type, voter, parent_object):
    """
    Creates a vote node that we can use to track reputation changes over time
    for users.
    This node is hooked up to the object that has been voted on and the
    user that voted. The node is created every time someone votes and does not
    get updated when someone changes their vote, it just makes a new one, this
    may not be the final functionality but this is the current implementation.

    :param node_id:
    :param vote_type:
    :param voter:
    :param parent_object:
    :return:
    """
    sb_object = get_parent_votable_content(parent_object)
    try:
        current_pleb = Pleb.get(username=voter)
    except (DoesNotExist, Pleb.DoesNotExist, CypherException, ClientError,
            IOError) as e:
        raise create_vote_node.retry(exc=e, countdown=10, max_retries=None)
    try:
        owner = Pleb.get(username=sb_object.owner_username)
    except (DoesNotExist, Pleb.DoesNotExist, CypherException, ClientError,
            IOError) as e:
        raise create_vote_node.retry(exc=e, countdown=10, max_retries=None)
    last_vote = sb_object.get_last_user_vote(current_pleb.username)
    if sb_object.visibility == 'public':
        if vote_type == 1:
            reputation_change = sb_object.up_vote_adjustment
        else:
            reputation_change = sb_object.down_vote_adjustment
    else:
        reputation_change = 0
    try:
        vote_node = Vote.nodes.get(object_uuid=node_id)
    except (Vote.DoesNotExist, DoesNotExist):
        vote_node = Vote(object_uuid=node_id, vote_type=vote_type,
                         reputation_change=reputation_change).save()
    if last_vote is None:
        sb_object.first_votes.connect(vote_node)
        sb_object.last_votes.connect(vote_node)
    else:
        sb_object.last_votes.disconnect(last_vote)
        last_vote.next_vote.connect(vote_node)
        sb_object.last_votes.connect(vote_node)
    vote_node.vote_on.connect(sb_object)
    vote_node.owned_by.connect(current_pleb)
    if not owner.last_counted_vote_node:
        owner.last_counted_vote_node = node_id
    owner.reputation_update_seen = False
    owner.save()
    cache.set(owner.username, owner)
    # See reputation_change method on pleb for where this is set
    cache.delete("%s_reputation_change" % owner.username)
    return True
