import pytz
from datetime import datetime

from plebs.neo_models import Pleb
from sb_comments.utils import get_post_comments
from .neo_models import SBPost
import sb_posts.tasks
#from .tasks import (delete_post_and_comments,create_downvote_post,
#                    create_upvote_post,edit_post_info_task)

def get_pleb_posts(pleb_object):
    try:
        pleb_posts = pleb_object.traverse('posts').run()
        return get_post_comments(pleb_posts)
    except:
        return {"details": "You have no posts!"}

def save_post(post_info):
    try:
        test_post = SBPost.index.get(post_id = post_info['post_id'])
    except SBPost.DoesNotExist:
        my_citizen = Pleb.index.get(email = post_info['pleb'])
        post_info.pop('pleb', None)
        my_post = SBPost(**post_info)
        my_post.save()
        wall = my_citizen.traverse('wall').run()[0]
        my_post.posted_on_wall.connect(wall)
        wall.post.connect(my_post)
        rel = my_post.owned_by.connect(my_citizen)
        rel.save()
        rel_from_pleb = my_citizen.posts.connect(my_post)
        rel_from_pleb.save()
        return True
    #determine who posted/shared/...

def edit_post_info(post_info):
    try:
        my_post = SBPost.index.get(post_id = post_info['post_uuid'])
        my_post.content = post_info['content']
        my_post.last_edited_on = datetime.now(pytz.utc)
        my_post.save()
        return True
    except SBPost.DoesNotExist:
        return False

def delete_post_info(post_info):
    try:
        my_post = SBPost.index.get(post_id = post_info['post_uuid'])
        post_comments = my_post.traverse('comments')
        for comment in post_comments:
            comment.delete()
        my_post.delete()
        return True
    except SBPost.DoesNotExist:
        return False


def create_post_vote(post_info):
    my_pleb = Pleb.index.get(email = post_info['pleb'])
    my_post = SBPost.index.get(post_id = post_info['post_uuid'])
    if my_post.up_voted_by.is_connected(my_pleb) or my_post.down_voted_by.is_connected(my_pleb):
        print "You have voted already!"
    else:
        if post_info['vote_type'] == 'up':
            sb_posts.tasks.create_upvote_post.apply_async([post_info,])
            print "Thanks for voting!"
        elif post_info['vote_type'] =='down':
            sb_posts.tasks.create_downvote_post.apply_async([post_info,])
            print "Thanks for voting!"

