from celery import shared_task

from django.core.cache import cache

from neomodel import db, DoesNotExist

from plebs.neo_models import Pleb
from sb_search.neo_models import Searchable
from .utils import update_view_count


@shared_task()
def update_view_count_task(object_uuid, username):
    try:
        profile = Pleb.get(username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise update_view_count_task.retry(exc=e, max_retries=5, countdown=45)

    sb_object = cache.get(object_uuid)
    if sb_object is None:
        sb_object = Searchable.nodes.get(object_uuid=object_uuid)

    query = 'MATCH (a:Pleb {username: "%s"})-[b:VIEWED]->' \
            ' (c:Searchable {object_uuid: "%s"}) RETURN b' % (
                username, object_uuid)
    res, col = db.cypher_query(query)
    if len(res) == 0:
        res = update_view_count(sb_object)
        if isinstance(res, Exception):
            raise update_view_count_task.retry(exc=res, countdown=5,
                                               max_retries=None)
        relationship = profile.viewed.connect(sb_object)
        sb_object.viewed_by.connect(profile)
    else:
        relationship = profile.viewed.relationship(sb_object)
    relationship.times_viewed += 1
    relationship.save()

    return True
