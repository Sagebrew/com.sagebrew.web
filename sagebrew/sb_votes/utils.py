from neomodel import db

from sagebrew.sb_docstore.utils import (get_vote, add_object_to_table,
                                        update_vote)


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

    if not res:
        add_object_to_table('votes', vote_data)
    else:
        update_vote(parent_object_uuid, username, status, now)
    return True


def create_vote_relationship(content_id, voter_username,
                             vote_active, vote_type):
    try:
        query = 'MATCH (v:VotableContent {object_uuid:"%s"}), ' \
                '(p:Pleb {username:"%s"}) ' \
                'CREATE UNIQUE (v)<-[vote:PLEB_VOTES]-(p) ' \
                'WITH v, vote, p SET vote.active=%s, ' \
                'vote.vote_type=%s RETURN v' % (
                    content_id, voter_username, vote_active, vote_type)
        res, _ = db.cypher_query(query)
    except Exception:
        query = 'MATCH (v:VotableContent {object_uuid:"%s"})' \
                '<-[vote:PLEB_VOTES]-(p:Pleb {username:"%s"}) ' \
                'SET vote.active=%s, vote.vote_type=%s RETURN v' % (
                    content_id, voter_username, vote_active, vote_type)
        res, _ = db.cypher_query(query)

    return res
