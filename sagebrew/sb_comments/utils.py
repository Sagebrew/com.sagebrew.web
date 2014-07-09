import pytz
from uuid import uuid1
from datetime import datetime

from .neo_models import SBComment
from sb_posts.neo_models import SBPost

from plebs.neo_models import Pleb
from .tasks import create_upvote_comment, create_downvote_comment


#TODO Some of the utils will be moved back to a task




def get_post_comments(post_info):
    '''
    gets all the posts posted by a user and all the comments attached to each post

    :param post_info:
    :return:
    '''
    comment_array = []
    post_array = []
    for post in post_info:
        post_comments = post.traverse('comments').run()
        post_owner = post.traverse('owned_by').run()[0]
        for comment in post_comments:
            comment_owner = comment.traverse('is_owned_by').run()[0]
            comment_dict = {'comment_content': comment.content, 'comment_id': comment.comment_id, 'comment_up_vote_number': comment.up_vote_number, 'comment_down_vote_number': comment.down_vote_number,'comment_last_edited_on': comment.last_edited_on, 'comment_owner': comment_owner.first_name+' '+comment_owner.last_name}
            comment_array.append(comment_dict)
        post_dict = {'content': post.content, 'post_id': post.post_id, 'up_vote_number': post.up_vote_number, 'down_vote_number': post.down_vote_number, 'last_edited_on': post.last_edited_on, 'post_owner': post_owner.first_name + ' ' + post_owner.last_name, 'comments': comment_array}
        post_array.append(post_dict)
        comment_array = []
    return post_array

def create_upvote_comment_util(comment_info):
    '''
    creates an upvote on a comment, this is called by a util or task which will regulate
    attempts to create multiple votes quickly
    :param comment_info:
    :return:
    '''
    my_comment = SBComment.index.get(comment_id = comment_info['comment_uuid'])
    my_pleb = Pleb.index.get(email = comment_info['pleb'])
    my_comment.up_vote_number += 1
    my_comment.up_voted_by.connect(my_pleb)
    my_comment.save()

def create_downvote_comment_util(comment_info):
    '''
    creates a downvote on a comment, this is called by a util or task which will regulate
    attempts to create multiple votes quickly
    :param comment_info:
    :return:
    '''
    my_comment = SBComment.index.get(comment_id = comment_info['comment_uuid'])
    my_pleb = Pleb.index.get(email = comment_info['pleb'])
    my_comment.down_vote_number += 1
    my_comment.down_voted_by.connect(my_pleb)
    my_comment.save()

def create_comment_vote(comment_info):
    '''
    determines whether or not the user has voted on the comment before and only allows
    them to vote if they have not voted
    :param comment_info:
    :return:
    '''
    #TODO This needs to allow to changing of vote
    my_pleb = Pleb.index.get(email = comment_info['pleb'])
    my_comment = SBComment.index.get(comment_id = comment_info['comment_uuid'])
    print comment_info['vote_type']
    if my_comment.up_voted_by.is_connected(my_pleb) or my_comment.down_voted_by.is_connected(my_pleb):
        print "You have voted already!"
    else:
        if comment_info['vote_type'] == 'up':
            create_upvote_comment_util(comment_info)
            print "Thanks for voting"
        elif comment_info['vote_type'] == 'down':
            create_downvote_comment_util(comment_info)
            print "Thanks for voting"

def save_comment(comment_info):
    '''
    Creates a comment with the content passed to it. It also connects the comment
    to the post it was attached to and the user which posted it
    :param comment_info:
    :return:
    '''
    my_citizen = Pleb.index.get(email = comment_info['pleb'])
    parent_object = SBPost.index.get(post_id = comment_info['post_uuid'])
    comment_info.pop('post_uuid', None)
    comment_info.pop('pleb', None)
    comment_info['comment_id'] = uuid1()
    my_comment = SBComment(**comment_info)
    my_comment.save()
    rel_to_pleb = my_comment.is_owned_by.connect(my_citizen)
    rel_to_pleb.save()
    rel_from_pleb = my_citizen.comments.connect(my_comment)
    rel_from_pleb.save()
    rel_to_post = my_comment.commented_on_post.connect(parent_object)
    rel_to_post.save()
    rel_from_post = parent_object.comments.connect(my_comment)
    rel_from_post.save()
    #determine who referenced/shared/...

def edit_comment_util(comment_info, edited_on):
    '''
    finds the comment with the given comment id then changes the content to the
    content which was passed. also changes the edited on date and time to the
    current time, it also checks to make sure that a comment wont get edited
    if the time is earlier than the last time it was edited, this ensures
    that
    :param comment_info:
    :param edited_on:
    :return:
    '''
    my_comment = SBComment.index.get(comment_id = comment_info['comment_uuid'])
    if my_comment.last_edited_on > edited_on:
        return False
    my_comment.content = comment_info['content']
    my_comment.last_edited_on = edited_on
    my_comment.save()
    return True

def delete_comment_util(comment_info):
    my_comment = SBComment.index.get(comment_id = comment_info['comment_uuid'])
    my_comment.delete()

