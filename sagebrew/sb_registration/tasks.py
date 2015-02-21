from celery import shared_task
from neomodel.exception import DoesNotExist, CypherException

from plebs.neo_models import Pleb
from sb_tag.neo_models import SBTag

@shared_task()
def update_interests(email, interests):
    try:
        citizen = Pleb.nodes.get(email)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise update_interests.retry(exc=e, countdown=3, max_retries=None)
    except (CypherException, IOError) as e:
        raise update_interests.retry(exc=e, countdown=3, max_retries=None)
    for interest in interests:
        if interests[interest] is True:
            try:
                tag = SBTag.nodes.get(tag_name=interest)
                citizen.interests.connect(tag)
            except (SBTag.DoesNotExist, DoesNotExist) as e:
                raise update_interests.retry(exc=e, countdown=3,
                                             max_retries=None)
            except (CypherException, IOError) as e:
                raise update_interests.retry(exc=e, countdown=3,
                                             max_retries=None)
    return True