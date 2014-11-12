import logging
from uuid import uuid1
from json import dumps
from neomodel import CypherException

from .neo_models import SBComment
from api.utils import execute_cypher_query

logger = logging.getLogger('loggly_logs')


def get_post_comments(post_info):
    '''
    gets all the posts posted by a user and all the comments attached to
    each post

    :param post_info:
                    post_info is an array of SBPost objects
    :return:
    '''
    comment_array = []
    post_array = []
    for post in post_info:
        query = 'MATCH (p:SBPost) WHERE p.sb_id="%s" ' \
                'WITH p MATCH (p) - [:HAS_A] - (c:SBComment) ' \
                'WHERE c.to_be_deleted=False ' \
                'WITH c ORDER BY c.created_on ' \
                'RETURN c' % post.sb_id
        post_comments, meta = execute_cypher_query(query)
        post_comments = [SBComment.inflate(row[0]) for row in post_comments]
        post_owner = post.owned_by.all()[0]
        post.view_count += 1
        post.save()
        for comment in post_comments:
            comment_owner = comment.is_owned_by.all()[0]
            comment_dict = {'comment_content': comment.content,
                            'comment_up_vote_number': comment.get_upvote_count(),
                            'vote_count': comment.get_vote_count(),
                            'sb_id': comment.sb_id,
                            'comment_down_vote_number':
                                comment.get_downvote_count(),
                            'comment_last_edited_on':
                                str(comment.last_edited_on),
                            'comment_owner': comment_owner.first_name + ' '
                                             + comment_owner.last_name,
                            'comment_owner_email': comment_owner.email}
            comment.view_count += 1
            comment.save()
            comment_array.append(comment_dict)
        post_dict = {'content': post.content, 'sb_id': post.sb_id,
                     'vote_count': post.get_vote_count(),
                     'up_vote_number': post.get_upvote_count(),
                     'down_vote_number': post.get_downvote_count(),
                     'last_edited_on': str(post.last_edited_on),
                     'post_owner': post_owner.first_name + ' ' +
                                   post_owner.last_name,
                     'post_owner_email': post_owner.email,
                     'comments': comment_array}
        post_array.append(post_dict)
        comment_array = []
    return post_array


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
