from uuid import uuid1

from .neo_models import SBPost
from plebs.neo_models import Pleb

from celery import shared_task

@shared_task()
def save_post(post_info):
    my_citizen = Pleb.index.get(email = post_info['pleb'])
    print post_info
    post_info.pop('pleb', None)
    post_id = uuid1()
    post_info['post_id'] = str(post_id)
    print post_info
    my_post = SBPost(**post_info)
    my_post.save()
    rel = my_post.owned_by.connect(my_citizen)
    rel.save()
    rel_from_pleb = my_citizen.posts.connect(my_post)
    rel_from_pleb.save()
    #determine who posted/shared/...

