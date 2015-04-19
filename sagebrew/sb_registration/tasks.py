from celery import shared_task
from neomodel import (DoesNotExist, AttemptedCardinalityViolation,
                      CypherException)

from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from plebs.neo_models import Address


@shared_task()
def update_interests(username, interests):
    try:
        citizen = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise update_interests.retry(exc=e, countdown=3, max_retries=None)
    except (CypherException, IOError) as e:
        raise update_interests.retry(exc=e, countdown=3, max_retries=None)
    for key, value in interests.iteritems():
        if value is True or value != []:
            try:
                tag = Tag.nodes.get(name=key.lower())
                citizen.interests.connect(tag)
            except (Tag.DoesNotExist, DoesNotExist) as e:
                raise update_interests.retry(exc=e, countdown=3,
                                             max_retries=None)
            except (CypherException, IOError) as e:
                raise update_interests.retry(exc=e, countdown=3,
                                             max_retries=None)
    return True


@shared_task()
def store_address(username, address_clean):
    try:
        citizen = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise store_address.retry(exc=e, countdown=3, max_retries=None)
    except (CypherException, IOError) as e:
        raise store_address.retry(exc=e, countdown=3, max_retries=None)
    try:
        address = Address(street=address_clean['primary_address'],
                          street_aditional=address_clean[
                              'street_additional'],
                          city=address_clean['city'],
                          state=address_clean['state'],
                          postal_code=address_clean['postal_code'],
                          latitude=address_clean['latitude'],
                          longitude=address_clean['longitude'],
                          congressional_district=address_clean[
                              'congressional_district'])
        address.save()
    except (CypherException, IOError) as e:
        raise store_address.retry(exc=e, countdown=3, max_retries=None)

    try:
        address.owned_by.connect(citizen)
        citizen.address.connect(address)
        citizen.determine_reps()
    except AttemptedCardinalityViolation:
        pass
    except (CypherException, IOError) as e:
        raise store_address.retry(exc=e, countdown=3, max_retries=None)
    return True


@shared_task()
def save_profile_picture(url, username):
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        raise save_profile_picture.retry(exc=e, countdown=3, max_retries=None)
    try:
        pleb.profile_pic = url
        pleb.save()
    except CypherException as e:
        raise save_profile_picture.retry(exc=e, countdown=3, max_retries=None)
    return True
