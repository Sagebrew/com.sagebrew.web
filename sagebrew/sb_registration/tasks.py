from celery import shared_task
from localflavor.us.us_states import US_STATES

from django.core.cache import cache

from neomodel import (DoesNotExist, AttemptedCardinalityViolation,
                      CypherException)

from api.utils import spawn_task
from plebs.tasks import update_address_location
from plebs.neo_models import Pleb, Address


@shared_task()
def store_address(username, address_clean):
    try:
        citizen = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise store_address.retry(exc=e, countdown=3, max_retries=None)
    except (CypherException, IOError) as e:
        raise store_address.retry(exc=e, countdown=3, max_retries=None)
    try:
        try:
            state = dict(US_STATES)[address_clean['state']]
        except KeyError:
            return address_clean['state']
        address = Address(street=address_clean['primary_address'],
                          street_aditional=address_clean[
                              'street_additional'],
                          city=address_clean['city'],
                          state=state,
                          postal_code=address_clean['postal_code'],
                          latitude=address_clean['latitude'],
                          longitude=address_clean['longitude'],
                          congressional_district=address_clean[
                              'congressional_district'],
                          county=address_clean['county']).save()
    except (CypherException, IOError) as e:
        raise store_address.retry(exc=e, countdown=3, max_retries=None)

    try:
        address.owned_by.connect(citizen)
        citizen.address.connect(address)
        citizen.determine_reps()
        spawn_task(task_func=update_address_location,
                   task_param={"object_uuid": address.object_uuid})
    except AttemptedCardinalityViolation:
        pass
    except (CypherException, IOError) as e:
        raise store_address.retry(exc=e, countdown=3, max_retries=None)
    cache.delete(username)
    return True


@shared_task()
def save_profile_picture(url, username):
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise save_profile_picture.retry(exc=e, countdown=3, max_retries=None)
    try:
        pleb.profile_pic = url
        pleb.save()
        cache.delete(pleb.username)
    except (CypherException, IOError) as e:
        raise save_profile_picture.retry(exc=e, countdown=3, max_retries=None)
    return True
