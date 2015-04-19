from celery import shared_task

from django.conf import settings

from neomodel.exception import DoesNotExist, CypherException

from sb_public_official.neo_models import BaseOfficial
from sb_public_official.utils import get_rep_type

from .utils import (add_object_to_table, build_rep_page)


@shared_task()
def add_object_to_table_task(object_data, table):
    res = add_object_to_table(table_name=table, object_data=object_data)
    if isinstance(res, Exception) is True:
        raise add_object_to_table_task.retry(exc=res, countdown=3,
                                             max_retries=None)
    return True


@shared_task()
def build_rep_page_task(rep_id, rep_type=None):
    if rep_type is None:
        try:
            rep = BaseOfficial.nodes.get(object_uuid=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            raise build_rep_page_task.retry(exc=e, countdown=3,
                                            max_retries=None)
    else:
        r_type = get_rep_type(dict(settings.BASE_REP_TYPES)[rep_type])
        try:
            rep = r_type.nodes.get(object_uuid=rep_id)
        except (r_type.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
    res = build_rep_page(rep)
    if isinstance(res, Exception):
        raise build_rep_page_task.retry(exc=res, countdown=3, max_retries=None)
    return True
