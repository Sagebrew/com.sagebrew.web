from neomodel import CypherException, DoesNotExist

from sb_base.decorators import apply_defense
from .neo_models import SBComment

@apply_defense
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
        my_comment = SBComment.nodes.get(sb_id=comment_uuid)
    except (SBComment.DoesNotExist, DoesNotExist):
        my_comment = SBComment(content=content, sb_id=comment_uuid)
        my_comment.save()
    except CypherException as e:
        return e
    return my_comment


@apply_defense
def comment_relations(pleb, comment, sb_object):
    comment_add_res = sb_object.comment_on(comment)
    if isinstance(comment_add_res, Exception) is True:
        return comment_add_res

    return pleb.relate_comment(comment)
