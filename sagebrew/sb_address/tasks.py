import us
import requests
from django.conf import settings

from celery import shared_task

from neo4j.v1 import CypherError
from neomodel import DoesNotExist, db

from sagebrew.api.utils import spawn_task
from sagebrew.sb_public_official.tasks import create_and_attach_state_level_reps
from sagebrew.sb_locations.neo_models import Location

from sagebrew.sb_address.neo_models import Address


@shared_task()
def update_address_location(object_uuid):
    try:
        address = Address.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Address.DoesNotExist, CypherError, IOError) as e:
        raise update_address_location.retry(exc=e, countdown=3,
                                            max_retries=None)
    try:
        state = us.states.lookup(address.state)
        district = address.congressional_district
        query = 'MATCH (a:Address {object_uuid:"%s"})-[r:ENCOMPASSED_BY]->' \
                '(l:Location) DELETE r' % object_uuid
        db.cypher_query(query)
        query = 'MATCH (s:Location {name:"%s"})-[:ENCOMPASSES]->' \
                '(d:Location {name:"%s", sector:"federal"}) RETURN d' % \
                (state, district)
        res, _ = db.cypher_query(query)
        if res.one is not None:
            district = Location.inflate(res.one)
            address.encompassed_by.connect(district)
        address.set_encompassing()
    except (CypherError, IOError) as e:
        raise update_address_location.retry(exc=e, countdown=3,
                                            max_retries=None)
    return True


@shared_task()
def connect_to_state_districts(object_uuid):
    try:
        address = Address.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Address.DoesNotExist, CypherError, IOError) as e:
        raise connect_to_state_districts.retry(exc=e, countdown=3,
                                               max_retries=None)
    try:
        lookup_url = settings.OPENSTATES_DISTRICT_SEARCH_URL % \
            (address.latitude, address.longitude) \
            + "&apikey=53f7bd2a41df42c082bb2f07bd38e6aa"
    except TypeError:
        # in case an address doesn't have a latitude or longitude
        return False
    response = requests.get(
        lookup_url, headers={"content-type": 'application/json; charset=utf8'})
    response_json = response.json()
    try:
        for rep in response_json:
            try:
                sector = 'state_%s' % rep['chamber']
                query = 'MATCH (l:Location {name: "%s", sector:"federal"})-' \
                        '[:ENCOMPASSES]->(district:Location {name:"%s", ' \
                        'sector:"%s"}) RETURN district ' % \
                        (us.states.lookup(address.state).name,
                         rep['district'], sector)
                res, _ = db.cypher_query(query)
            except KeyError:
                return False
            try:
                res = res[0]
            except IndexError as e:
                raise connect_to_state_districts.retry(exc=e, countdown=3,
                                                       max_retries=None)
            try:
                state_district = Location.inflate(res.district)
            except (CypherError, IOError) as e:
                raise connect_to_state_districts.retry(exc=e, countdown=3,
                                                       max_retries=None)
            if state_district not in address.encompassed_by:
                address.encompassed_by.connect(state_district)
        spawn_task(task_func=create_and_attach_state_level_reps,
                   task_param={"rep_data": response_json})
        return True
    except (CypherError, IOError) as e:
        raise connect_to_state_districts.retry(exc=e, countdown=3,
                                               max_retries=None)
