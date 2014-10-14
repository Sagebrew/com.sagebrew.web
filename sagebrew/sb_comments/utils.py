import pytz
import logging
from uuid import uuid1
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
        query = 'MATCH (p:SBPost) WHERE p.post_id="%s" ' \
                'WITH p MATCH (p) - [:HAS_A] - (c:SBComment) ' \
                'WHERE c.to_be_deleted=False ' \
                'WITH c ORDER BY c.created_on ' \
                'RETURN c' % post.post_id
        post_comments, meta = execute_cypher_query(query)
        post_comments = [SBComment.inflate(row[0]) for row in post_comments]
        post_owner = post.owned_by.all()[0]
        post.view_count += 1
        post.save()
        for comment in post_comments:
            comment_owner = comment.is_owned_by.all()[0]
            comment_dict = {'comment_content': comment.content,
                            'comment_up_vote_number': comment.up_vote_number,
                            'comment_id': comment.comment_id,
                            'comment_down_vote_number':
                                comment.down_vote_number,
                            'comment_last_edited_on': comment.last_edited_on,
                            'comment_owner': comment_owner.first_name + ' '
                                             + comment_owner.last_name,
                            'comment_owner_email': comment_owner.email}
            comment.view_count += 1
            comment.save()
            comment_array.append(comment_dict)
        post_dict = {'content': post.content, 'post_id': post.post_id,
                     'up_vote_number': post.up_vote_number,
                     'down_vote_number': post.down_vote_number,
                     'last_edited_on': post.last_edited_on,
                     'post_owner': post_owner.first_name + ' ' +
                                   post_owner.last_name,
                     'post_owner_email': post_owner.email,
                     'comments': comment_array}
        post_array.append(post_dict)
        comment_array = []
    return post_array

def create_upvote_comment_util(pleb="", comment_uuid=str(uuid1())):
    '''
    creates an upvote on a comment, this is called by a util or task which
    will regulate
    attempts to create multiple votes quickly

    :param comment_info:
                        pleb="" email of the user voting
                        comment_uuid=str(uuid) id of the comment being voted on
    :return:
    '''
    try:
        try:
            my_comment = SBComment.nodes.get(comment_id=comment_uuid)
        except SBComment.DoesNotExist:
            return False
        except DoesNotExist:
            return False
        try:
            my_pleb = Pleb.nodes.get(email=pleb)
        except Pleb.DoesNotExist:
            return False
        except DoesNotExist:
            return False
        my_comment.up_vote_number += 1
        my_comment.up_voted_by.connect(my_pleb)
        my_comment.save()
        return True
    except CypherException:
        logger.exception({"function": create_downvote_comment_util.__name__,
                          "exception": "CypherException: "})
        return False
    except Exception:
        logger.exception({"function": create_downvote_comment_util.__name__,
                          "exception": "UnhandledException: "})
        return None


def create_downvote_comment_util(pleb="", comment_uuid=str(uuid1())):
    '''
    creates a downvote on a comment, this is called by a util or task which
    will regulate
    attempts to create multiple votes quickly
    :param comment_info:
                        pleb="" email of the user voting
                        comment_uuid=str(uuid) id of the comment being voted on
    :return:
    '''
    try:
        try:
            my_comment = SBComment.nodes.get(comment_id=comment_uuid)
        except SBComment.DoesNotExist:
            return False
        except DoesNotExist:
            return False
        try:
            my_pleb = Pleb.nodes.get(email=pleb)
        except Pleb.DoesNotExist:
            return False
        except DoesNotExist:
            return False
        my_comment.down_vote_number += 1
        my_comment.down_voted_by.connect(my_pleb)
        my_comment.save()
        return True
    except CypherException:
        logger.exception({"function": create_downvote_comment_util.__name__,
                          "exception": "CypherException: "})
        return False
    except Exception:
        logger.exception({"function": create_downvote_comment_util.__name__,
                          "exception": "UnhandledException: "})
        return None


def save_comment_post(content="", pleb="", post_uuid=str(uuid1())):
    '''
    Creates a comment with the content passed to it. It also connects the
    comment
    to the post it was attached to and the user which posted it
    :param comment_info:
                        content="" the content of the comment
                        pleb="" email of the person submitting the comment
                        post_uuid = str(uuid) id of the post which the
                        comment will be attached to
    :return:
    '''
    try:
        try:
            my_citizen = Pleb.nodes.get(email=pleb)
        except Pleb.DoesNotExist:
            return False
        except DoesNotExist:
            return False
        try:
            parent_object = SBPost.nodes.get(post_id=post_uuid)
        except SBPost.DoesNotExist:
            return False
        except DoesNotExist:
            return False
        comment_uuid = str(uuid1())
        my_comment = SBComment(content=content, comment_id=comment_uuid)
        my_comment.save()
        rel_to_pleb = my_comment.is_owned_by.connect(my_citizen)
        rel_to_pleb.save()
        rel_from_pleb = my_citizen.comments.connect(my_comment)
        rel_from_pleb.save()
        rel_to_post = my_comment.commented_on_post.connect(parent_object)
        rel_to_post.save()
        rel_from_post = parent_object.comments.connect(my_comment)
        rel_from_post.save()
        return my_comment
    except CypherException:
        logger.exception({"function": save_comment_post.__name__,
                          "exception": "CypherException: "})
        return False
    except Exception:
        return None

def edit_comment_util(comment_uuid=str(uuid1()), content="",
                      last_edited_on=None, pleb=""):
    '''
    finds the comment with the given comment id then changes the content to the
    content which was passed. also changes the edited on date and time to the
    current time, it also checks to make sure that a comment wont get edited
    if the time is earlier than the last time it was edited, this ensures
    that
    :param comment_info:
                        comment_uuid=str(uuid) id of the comment to be edited
                        content="" content which the comment should be
                        changed to
    :param edited_on:
                    DateTime which the util was called
    :return:
    '''
    try:
        my_comment = SBComment.nodes.get(comment_id=comment_uuid)

        if my_comment.last_edited_on > last_edited_on:
            return False

        if my_comment.content == content:
            return False

        if my_comment.last_edited_on == last_edited_on:
            return False

        if my_comment.to_be_deleted:
            return False

        my_comment.content = content
        my_comment.last_edited_on = last_edited_on
        my_comment.save()
        return True
    except SBComment.DoesNotExist:
        return {'detail': "retry"}
    except DoesNotExist:
        return {'detail': 'retry'}
    except Exception:
        logger.exception({"function": edit_comment_util.__name__,
                          'exception': "UnhandledException: "})
        return {'exception', 'retry'}

def delete_comment_util(comment_uuid=str(uuid1())):
    '''
    deletes the comment which is tied to the id it is passed

    :param comment_uuid:
                        id of the comment which will be deleted
    :return:
    '''
    try:
        my_comment = SBComment.nodes.get(comment_id=comment_uuid)
        if datetime.now(pytz.utc).day - my_comment.delete_time.day >= 1:
            my_comment.delete()
            return True
        else:
            return True
    except SBComment.DoesNotExist:
        return False
    except DoesNotExist:
        return False

def flag_comment_util(comment_uuid, current_user, flag_reason):
    '''
    Attempts to get the comment and user from the parameters then creates the
    connection between them of having been flagged, also increases the number
    of flags it has based on what reason was passed

    :param comment_uuid:
    :param current_user:
    :param flag_reason:
    :return:
    '''
    try:
        try:
            comment = SBComment.nodes.get(comment_id=comment_uuid)
        except SBComment.DoesNotExist:
            return None
        except DoesNotExist:
            return None

        try:
            pleb = Pleb.nodes.get(email=current_user)
        except Pleb.DoesNotExist:
            return False
        except DoesNotExist:
            return False

        if comment.flagged_by.is_connected(pleb):
            return False

        if flag_reason=='spam':
            comment.flagged_by.connect(pleb)
            comment.flagged_as_spam_count += 1
            comment.save()
        elif flag_reason == 'explicit':
            comment.flagged_by.connect(pleb)
            comment.flagged_as_explicit_count += 1
            comment.save()
        elif flag_reason == 'other':
            comment.flagged_by.connect(pleb)
            comment.flagged_as_other_count += 1
            comment.save()
        else:
            return False
        return True
    except Exception:
        logger.exception('UnhandledException: ')
        return None

