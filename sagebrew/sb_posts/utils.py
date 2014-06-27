import pytz
from datetime import datetime
from uuid import uuid1

from plebs.neo_models import Pleb
from .neo_models import SBPost
from .tasks import (delete_post_and_comments, create_downvote_post, create_upvote_post)

def get_pleb_posts(pleb_object):
    post_array = []
    try:
        pleb_posts = pleb_object.traverse('posts').run()
        for item in pleb_posts:
            post_dict = {'content': item.content, 'post_id': item.post_id, 'up_vote_number': item.up_vote_number, 'down_vote_number': item.down_vote_number, 'last_edited_on': item.last_edited_on}
            post_array.append(post_dict)
        return post_array
    except:
        print "You have no posts!"

def save_post(post_info):
    my_citizen = Pleb.index.get(email = post_info['pleb'])
    post_info.pop('pleb', None)
    post_id = uuid1()
    post_info['post_id'] = str(post_id)
    my_post = SBPost(**post_info)
    my_post.save()
    rel = my_post.owned_by.connect(my_citizen)
    rel.save()
    rel_from_pleb = my_citizen.posts.connect(my_post)
    rel_from_pleb.save()
    #determine who posted/shared/...

def edit_post_info(post_info):
    my_post = SBPost.index.get(post_id = post_info['post_uuid'])
    my_post.content = post_info['content']
    my_post.last_edited_on = datetime.now(pytz.utc)
    my_post.save()

def delete_post_info(post_info):
    delete_post_and_comments(post_info)
    print "Your post and all comments will be deleted"

def create_post_vote(post_info):
    if post_info['vote_type'] == 'up':
        create_upvote_post.apply_async([post_info,])
        print "Thanks for voting!"
    elif post_info['vote_type'] =='down':
        create_downvote_post.apply_async([post_info,])
        print "Thanks for voting!"

