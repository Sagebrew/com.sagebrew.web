from uuid import uuid1
from celery import shared_task

from django.template.loader import render_to_string
from django.core.cache import cache

from neomodel import CypherException, DoesNotExist, UniqueProperty
from py2neo.cypher.error.statement import ClientError

from api.utils import spawn_task, smart_truncate
from plebs.tasks import update_reputation
from plebs.neo_models import Pleb
from sb_base.neo_models import (get_parent_votable_content,
                                get_parent_titled_content)
from sb_notifications.tasks import spawn_notifications

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
    :param sb_object:
    :return:
    """
    try:
        current_pleb = Pleb.get(username=current_pleb)
    except (DoesNotExist, Pleb.DoesNoteExist, CypherException, IOError) as e:
        raise vote_object_task.retry(exc=e, countdown=10, max_retries=None)
    sb_object = get_parent_votable_content(object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise vote_object_task.retry(exc=sb_object, countdown=10,
                                     max_retries=None)
    res = sb_object.vote_content(vote_type, current_pleb)

    if isinstance(res, Exception) is True:
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)

    res = spawn_task(update_reputation, {"username": sb_object.owner_username})

    if isinstance(res, Exception):
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)

    return sb_object


@shared_task()
def object_vote_notifications(object_uuid, previous_vote_type, new_vote_type,
                              voting_pleb):
    sb_object = get_parent_votable_content(object_uuid)
    try:
        current_pleb = Pleb.get(username=voting_pleb)
    except (DoesNotExist, Pleb.DoesNoteExist, CypherException, ClientError,
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
        res = spawn_task(spawn_notifications, task_param={
            'from_pleb': current_pleb.username,
            'to_plebs': [sb_object.owner_username],
            'sb_object': sb_object.object_uuid,
            'notification_id': str(uuid1()),
            'url': sb_object.url,
            'action_name': action_name,
            'public': public
        })
        if isinstance(res, Exception):
            raise object_vote_notifications.retry(exc=res, countdown=10,
                                                  max_retries=None)
    return True


@shared_task()
def create_vote_node(node_id, vote_type, voter, parent_object):
    from logging import getLogger
    logger = getLogger('loggly_logs')
    '''
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
    '''
    sb_object = get_parent_votable_content(parent_object)
    try:
        current_pleb = Pleb.get(username=voter)
    except (DoesNotExist, Pleb.DoesNoteExist, CypherException, ClientError,
            IOError) as e:
        raise object_vote_notifications.retry(exc=e, countdown=10,
                                              max_retries=None)
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
    last_vote = sb_object.get_last_user_vote(current_pleb.username)
    logger.info(last_vote)
    if not last_vote:
        sb_object.first_votes.connect(vote_node)
        sb_object.last_votes.connect(vote_node)
    else:
        sb_object.last_votes.disconnect(last_vote)
        last_vote.next_vote.connect(vote_node)
        sb_object.last_votes.connect(vote_node)
    vote_node.vote_on.connect(sb_object)
    vote_node.owned_by.connect(current_pleb)
    cache.delete("%s_reputation_change" % parent_object.owner_username)
    return True
