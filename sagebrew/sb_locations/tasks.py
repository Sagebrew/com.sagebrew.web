from celery import shared_task

from django.core.cache import cache

from api.utils import spawn_task

from .utils import parse_google_places, connect_related_element


@shared_task()
def create_location_tree(external_id):
    hierarchy = cache.get(external_id)
    try:
        if hierarchy is None:
            raise KeyError("Could not find external id")
    except KeyError as e:
        raise create_location_tree.retry(exc=e, countdown=10,
                                         max_retries=None)
    end_node = parse_google_places(hierarchy['address_components'], external_id)
    spawn_task(task_func=connect_location_to_element, task_param={
        "element_id": external_id, "location": end_node})

    return True


@shared_task()
def connect_location_to_element(location, element_id):
    try:
        connect_related_element(location, element_id)
    except KeyError as e:
        raise connect_location_to_element.retry(exc=e, countdown=10,
                                                max_retries=None)
