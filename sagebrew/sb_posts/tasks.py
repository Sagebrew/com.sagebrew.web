from uuid import uuid1

from .neo_models import SBPost
from plebs.neo_models import Pleb

from celery import shared_task

#TODO separate functions to delete posts and comments and votes
@shared_task()
def delete_post_and_comments(post_info):
    my_post = SBPost.index.get(post_id = post_info['post_uuid'])
    post_comments = my_post.traverse('comments')
    for comment in post_comments:
        comment.delete()
    my_post.delete()

#TODO only allow plebs to create 1 vote but can then change vote
@shared_task()
def create_upvote_post(post_info):
    my_post = SBPost.index.get(post_id = post_info['post_uuid'])
    my_pleb = Pleb.index.get(email = post_info['pleb'])
    my_post.up_vote_number += 1
    my_post.up_voted_by.connect(my_pleb)
    my_post.save()

#TODO only allow plebs to create 1 vote but can then change vote
@shared_task()
def create_downvote_post(post_info):
    my_post = SBPost.index.get(post_id = post_info['post_uuid'])
    my_pleb = Pleb.index.get(email = post_info['pleb'])
    my_post.down_vote_number += 1
    my_post.down_voted_by.connect(my_pleb)
    my_post.save()

