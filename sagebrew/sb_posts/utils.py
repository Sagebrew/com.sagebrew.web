import pytz
from uuid import uuid1
from datetime import datetime

from plebs.neo_models import Pleb
from sb_comments.utils import get_post_comments
from .neo_models import SBPost

def get_pleb_posts(pleb_object):
    '''
    Gets all the posts which are attached to the page users wall aswell as the
    comments associated with the posts

    :param pleb_object:
                        This is an instance of a Pleb object
    :return:
    '''
    try:
        pleb_wall = pleb_object.traverse('wall').run()[0]
        pleb_posts = pleb_wall.traverse('post').run()
        return get_post_comments(pleb_posts)
    except:
        print "failed to retrieve posts"
        return {"details": "You have no posts!"}

def save_post(post_id=str(uuid1()),content="",current_pleb="",wall_pleb=""):
    '''
    saves a post and creates the relationships between the wall
    and the poster of the comment


    :param post_info:
                    post_id: str(uuid)
                    content: ""
                    current_pleb: email  (string)
                    wall_pleb: email  (string)
    :return: if post exists returns None
    else returns SBPost object
    '''
    try:
        test_post = SBPost.index.get(post_id = post_id)
        return None
    except SBPost.DoesNotExist:
        poster = Pleb.index.get(email = current_pleb)
        my_citizen = Pleb.index.get(email = wall_pleb)
        my_post = SBPost(content=content,post_id=post_id)
        my_post.save()
        wall = my_citizen.traverse('wall').run()[0]
        my_post.posted_on_wall.connect(wall)
        wall.post.connect(my_post)
        rel = my_post.owned_by.connect(poster)
        rel.save()
        rel_from_pleb = poster.posts.connect(my_post)
        rel_from_pleb.save()
        return my_post
    #determine who posted/shared/...

def edit_post_info(content="", post_uuid=str(uuid1())):
    '''
    changes the content of the post linked to the id passed to the function
    to the content which was passed

    :param post_info:
                    content: ""
                    post_uuid = str(uuid)
    :return:
    '''
    try:
        my_post = SBPost.index.get(post_id = post_uuid)
        my_post.content = content
        my_post.last_edited_on = datetime.now(pytz.utc)
        my_post.save()
        return my_post
    except SBPost.DoesNotExist:
        return False

def delete_post_info(post_uuid=str(uuid1())):
    '''
    deletes the post and all comments attached to it

    :param post_info:
                    post_uuid = str(uuid1)
    :return:
    '''
    try:
        my_post = SBPost.index.get(post_id = post_uuid)
        post_comments = my_post.traverse('comments')
        for comment in post_comments:
            comment.delete()
        my_post.delete()
        return True
    except SBPost.DoesNotExist:
        return False


def create_post_vote(pleb="", post_uuid=str(uuid1()), vote_type=""):
    '''
    determines if the user has voted on this post yet, if not then it allows
    the vote and creates it, if not it does not allow.

    :param post_info:
                    pleb = "" email
                    post_uuid = str(uuid)
                    vote_type = "" up/down
    :return:
    '''
    #TODO This needs to allow to changing of vote
    from sb_posts.tasks import create_downvote_post, create_upvote_post
    my_pleb = Pleb.index.get(email = pleb)
    my_post = SBPost.index.get(post_id = post_uuid)
    if my_post.up_voted_by.is_connected(my_pleb) or my_post.down_voted_by.is_connected(my_pleb):
        print "You have voted already!"
    else:
        if vote_type == 'up':
            create_upvote_post.apply_async([post_uuid,pleb,])
            print "Thanks for voting!"
        elif vote_type =='down':
            create_downvote_post.apply_async([post_uuid,pleb,])
            print "Thanks for voting!"

