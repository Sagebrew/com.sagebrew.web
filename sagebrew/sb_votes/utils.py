import logging
from json import dumps


logger = logging.getLogger("loggly_logs")

def vote_object_util(vote_type, current_pleb, sb_object):
    '''
    This function takes a pleb object, an
    sb_object(SBAnswer, SBQuestion, SBComment, SBPost), and a
    vote_type("up", "down"). It handles addition of a vote to an object.
    If the user has already voted it allows for changing the vote
    or removing the vote.

    :param vote_type:
    :param current_pleb:
    :param sb_object:
    :return:
    '''
    try:
        if vote_type=="up":
            if sb_object.up_voted_by.is_connected(current_pleb):
                sb_object.up_voted_by.disconnect(current_pleb)
                sb_object.up_vote_number -= 1
            elif sb_object.down_voted_by.is_connected(current_pleb):
                sb_object.down_voted_by.disconnect(current_pleb)
                sb_object.up_voted_by.connect(current_pleb)
                sb_object.down_vote_number -= 1
                sb_object.up_vote_number += 1
            else:
                sb_object.up_voted_by.connect(current_pleb)
                sb_object.up_vote_number += 1

        elif vote_type=="down":
            if sb_object.down_voted_by.is_connected(current_pleb):
                sb_object.down_voted_by.disconnect(current_pleb)
                sb_object.down_vote_number -= 1
            elif sb_object.up_voted_by.is_connected(current_pleb):
                sb_object.up_voted_by.disconnect(current_pleb)
                sb_object.down_voted_by.connect(current_pleb)
                sb_object.down_vote_number += 1
                sb_object.up_vote_number -= 1
            else:
                sb_object.down_voted_by.connect(current_pleb)
                sb_object.down_vote_number += 1

        else:
            return False
        sb_object.save()
        return True
    except Exception as e:
        logger.exception(dumps({"function": vote_object_util.__name__,
                                "exception": "Unhandled Exception"}))
        return e

