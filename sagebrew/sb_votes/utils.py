from uuid import uuid1

from api.utils import spawn_task
from sb_docstore.utils import get_vote, add_object_to_table, update_vote


def determine_update_values(prev_status, update_status, upvote_value,
                            downvote_value):
    if update_status == 2 and prev_status == 1:
        upvote_value -= 1
    elif update_status == 2 and prev_status == 0:
        downvote_value -= 1
    elif update_status == 1 and prev_status == 0:
        downvote_value -= 1
        upvote_value += 1
    elif update_status == 0 and prev_status == 1:
        downvote_value += 1
        upvote_value -= 1
    elif update_status == 1 and prev_status == 2:
        upvote_value += 1
    elif update_status == 0 and prev_status == 2:
        downvote_value += 1
    return upvote_value, downvote_value


def determine_vote_type(object_uuid, username):
    vote_type = get_vote(object_uuid, username)
    if isinstance(vote_type, Exception):
        return vote_type
    if vote_type is not None:
        if vote_type['status'] == 2:
            vote_type = None
        else:
            vote_type = bool(vote_type['status'])
    return vote_type


def handle_vote(parent_object_uuid, status, username, now):
    from sb_votes.tasks import (object_vote_notifications, create_vote_node)
    vote_data = {
        "parent_object": parent_object_uuid,
        "user": username,
        "status": status,
        "time": now
    }
    res = get_vote(parent_object_uuid, user=username)

    if not res:
        add_object_to_table('votes', vote_data)
        previous_vote = None
        new_vote = status
    else:
        update, previous_vote = update_vote(parent_object_uuid, username,
                                            status, now)
        new_vote = update['status']
    try:
        previous_vote = int(previous_vote)
    except TypeError:
        previous_vote = None
    spawn_task(task_func=object_vote_notifications,
               task_param={
                   "object_uuid": parent_object_uuid,
                   "previous_vote_type": previous_vote,
                   "new_vote_type": new_vote,
                   "voting_pleb": username
               })
    if previous_vote != new_vote:
        spawn_task(task_func=create_vote_node,
                   task_param={
                       "node_id": str(uuid1()),
                       "vote_type": new_vote,
                       "voter": username,
                       "parent_object": parent_object_uuid
                   })
    return True
