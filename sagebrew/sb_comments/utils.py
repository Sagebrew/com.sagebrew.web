from datetime import datetime

from neomodel import CypherException, DoesNotExist

from sb_base.decorators import apply_defense
from sb_docstore.utils import get_vote_count

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
        my_comment = SBComment.nodes.get(object_uuid=comment_uuid)
    except (SBComment.DoesNotExist, DoesNotExist):
        my_comment = SBComment(content=content, object_uuid=comment_uuid)
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


# TODO is there anyway to include this as a self. reference on a class of
# somesort. So that we don't have convert_dynamo_comment,
# convert_dynamo_solution, etc and just have DynamoTable.to_dict or something.
def convert_dynamo_comments(raw_comments):
    comments = []
    for comment in raw_comments:
        comment = dict(comment)
        comment['upvotes'] = get_vote_count(comment['object_uuid'],1)
        comment['downvotes'] = get_vote_count(
            comment['object_uuid'],0)
        comment['last_edited_on'] = datetime.strptime(
            comment['last_edited_on'][:len(comment['last_edited_on']) - 6],
            '%Y-%m-%d %H:%M:%S.%f')
        comment['created'] = datetime.strptime(
            comment['created'][:len(comment['created']) - 6],
            '%Y-%m-%d %H:%M:%S.%f')
        comment['vote_count'] = str(
            comment['upvotes'] - comment['downvotes'])
        comments.append(comment)
    return comments