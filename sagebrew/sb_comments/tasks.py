from uuid import uuid1

from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb

from celery import shared_task

@shared_task()
def save_comment(comment_info):
    my_citizen = Pleb.index.get(email = comment_info['pleb'])
    parent_object = SBPost.index.get(post_id = comment_info['post_uuid'])
    print parent_object.content
    comment_info.pop('post_uuid', None)
    comment_info.pop('pleb', None)
    comment_info['comment_id'] = uuid1()
    print comment_info
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
    #determine who posted/shared/...

@shared_task()
def submit_comment_on_post(comment_info):
    pass

@shared_task()
def submit_comment_on_question(comment_info):
    pass

@shared_task()
def submit_comment_on_answer(comment_info):
    pass