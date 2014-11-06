import pytz
import logging
from uuid import uuid1
from json import dumps
from datetime import datetime
from neomodel import CypherException, DoesNotExist

from .neo_models import SBComment
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb
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
                            'comment_up_vote_number': comment.up_vote_number,
                            'sb_id': comment.sb_id,
                            'comment_down_vote_number':
                                comment.down_vote_number,
                            'comment_last_edited_on':
                                str(comment.last_edited_on),
                            'comment_owner': comment_owner.first_name + ' '
                                             + comment_owner.last_name,
                            'comment_owner_email': comment_owner.email}
            comment.view_count += 1
            comment.save()
            comment_array.append(comment_dict)
        post_dict = {'content': post.content, 'sb_id': post.sb_id,
                     'up_vote_number': post.up_vote_number,
                     'down_vote_number': post.down_vote_number,
                     'last_edited_on': str(post.last_edited_on),
                     'post_owner': post_owner.first_name + ' ' +
                                   post_owner.last_name,
                     'post_owner_email': post_owner.email,
                     'comments': comment_array}
        post_array.append(post_dict)
        comment_array = []
    return post_array


def save_comment_post(content, pleb, post_uuid, comment_uuid=None):
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
        try:
            my_citizen = Pleb.nodes.get(email=pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False
        try:
            parent_object = SBPost.nodes.get(sb_id=post_uuid)
        except (SBPost.DoesNotExist, DoesNotExist) as e:
            return e
        my_comment = SBComment(content=content, sb_id=comment_uuid)
        my_comment.save()
        rel_to_pleb = my_comment.is_owned_by.connect(my_citizen)
        rel_to_pleb.save()
        rel_from_pleb = my_citizen.comments.connect(my_comment)
        rel_from_pleb.save()
        rel_from_post = parent_object.comments.connect(my_comment)
        rel_from_post.save()
        return my_comment
    except CypherException as e:
        return e
    except Exception as e:
        logger.exception(dumps({"function": save_comment_post.__name__,
                                "exception": "Unhandled Exception"}))
        return e

def delete_comment_util(comment_uuid):
    '''
    Removes the personal content the comment which is tied to the id it is
    passed

    :param comment_uuid:
                        id of the comment which will be deleted
    :return:
    '''
    try:
        my_comment = SBComment.nodes.get(sb_id=comment_uuid)
        if datetime.now(pytz.utc).day - my_comment.delete_time.day >= 1:
            my_comment.content = ""
            my_comment.save()
        return True
    except (SBComment.DoesNotExist, DoesNotExist) as e:
        return e
