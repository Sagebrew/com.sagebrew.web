import logging
from uuid import uuid1
from json import dumps
from neomodel import CypherException

from .neo_models import SBComment

logger = logging.getLogger('loggly_logs')


def save_comment(content, comment_uuid=None):
    '''
    Creates a comment with the content passed to it. It also connects the
    comment
    to the post it was attached to and the user which posted it
    :param content="" the content of the comment
    :param pleb="" email of the person submitting the comment
    :param post_uuid = str(uuid) id of the post which the
    :return:
    '''
    if comment_uuid is None:
        comment_uuid = str(uuid1())
    try:
        my_comment = SBComment(content=content, sb_id=comment_uuid)
        my_comment.save()
        return my_comment
    except CypherException as e:
        return e
    except Exception as e:
        logger.exception(dumps({"function": save_comment.__name__,
                                "exception": "Unhandled Exception"}))
        return e

def comment_relations(pleb, comment, sb_object):
    try:
        comment_add_res = sb_object.comment_on(comment)
        if isinstance(comment_add_res, Exception) is True:
            return comment_add_res

        pleb_res = pleb.relate_comment(comment)
        if isinstance(pleb_res, Exception) is True:
            return pleb_res

        return True
    except Exception as e:
        logger.exception(dumps({"function": comment_relations.__name__,
                                "exception": "Unhandled Exception:"}))
        return e
