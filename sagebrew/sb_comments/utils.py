from uuid import uuid1
from neomodel import CypherException

from sb_base.utils import defensive_exception
from .neo_models import SBComment


def save_comment(content, comment_uuid):
    '''
    Creates a comment with the content passed to it. It also connects the
    comment
    to the post it was attached to and the user which posted it
    :param content="" the content of the comment
    :param comment_uuid = str(uuid) id of the post which the
    :return:
    '''
    try:
        my_comment = SBComment(content=content, sb_id=comment_uuid)
        my_comment.save()
        return my_comment
    except CypherException as e:
        return e
    except Exception as e:
        return defensive_exception(save_comment.__name__, e, e)


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
        return defensive_exception(comment_relations.__name__, e, e)