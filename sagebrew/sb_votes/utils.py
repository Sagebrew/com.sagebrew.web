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
    vote_data = {
        "parent_object": parent_object_uuid,
        "user": username,
        "status": status,
        "time": now
    }
    res = get_vote(parent_object_uuid, user=username)
    if isinstance(res, Exception) is True:
        raise res
    if not res:
        add_res = add_object_to_table('votes', vote_data)
        if isinstance(add_res, Exception) is True:
            raise add_res
    else:
        update = update_vote(parent_object_uuid, username,
                             status, now)
        if isinstance(update, Exception) is True:
            raise update

    return True
