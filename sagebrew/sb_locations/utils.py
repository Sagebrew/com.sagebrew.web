from neomodel import db
from requests import get

from django.conf import settings

from .neo_models import Location


def parse_google_places(places, external_id):
    """
    The (regions) type collection instructs the Places service to return any
    result matching the following types:
        locality
        sublocality
        postal_code - We pop this since we don't use it
        country
        administrative_area_level_1
        administrative_area_level_2
    :param places:
    :param external_id:
    :return:
    """
    us_variants = ['United States', 'USA', 'US']
    country = None
    admin_area_1 = None
    admin_area_2 = None
    locality = None
    for place in places:
        if 'country' in place['types']:
            country = place
            if country['long_name'] in us_variants:
                country['long_name'] = "United States of America"
        elif 'administrative_area_level_1' in place['types']:
            admin_area_1 = place
        elif 'administrative_area_level_2' in place['types']:
            admin_area_2 = place
        elif ('administrative_area_level_3' in place['types'] or
                'locality' in place['types']):
            locality = place
    structure = verify_structure([
        country, admin_area_1, admin_area_2, locality], external_id)
    return create_tree(structure)


def google_maps_query(external_id):
    url = "https://maps.googleapis.com/maps/api/" \
                          "place/details/json?" \
                          "placeid=%s&key=%s" % (
                            external_id, settings.GOOGLE_MAPS_API_SERVER)
    response = get(url, headers={
        "content-type": "application/json"})
    return response.json()['result']['address_components']


def verify_structure(structure, external_id, verify=True):
    for idx, place in enumerate(structure):
        if place is None:
            # check to make sure we've actually hit the end and aren't just
            # missing an intermediate location due to Google not returning it
            for r_idx, remaining in enumerate(structure[idx+1:]):
                # If we aren't at the last node yet go ask Google again for
                # the full structure and restart the function with a flag that
                # stops us from constantly asking google
                if remaining is not None and verify is True:
                    return verify_structure(google_maps_query(external_id),
                                            external_id, False)
                elif verify is False:
                    # We've already been here and need to make due with what
                    # we have
                    pass
                elif r_idx + 1 == len(structure[idx+1:]):
                    # We're actually at the end. We should cut off the Nones
                    # and move on
                    structure = structure[:idx-1]
                    break


def create_tree(structure):
    # If top level node then check if exists, if it doesn't then create it
    parent_node = None
    for idx, element in enumerate(structure):
        # This could be generalized to just check the first in the list if
        # we are sure Google will always return a country, if we don't care
        # what the parent level node is (this is risky as it may result in
        # duplicates. For example if a state was the first element of the
        # structure), or if we wanted to add a flag that represented we
        # know this isn't labeled a country but google says it's the top of
        # the chain for this structure, and we may need to update it at a later
        # date.
        name = element['long_name']
        if idx == 0:
            # Could craft out a CREATE UNIQUE potentially but rather create
            # node with neomodel to get UUID and defaults set properly
            query = 'MATCH (a:Location {name: "%s"}) RETURN a' % name
            res, _ = db.cypher_query(query)
            if not res.one:
                parent_node = Location(name=name).save()
            else:
                parent_node = Location.inflate(res.one)
        else:
            # Otherwise take parent and see if it has any children with name
            #       (Check if any children at any depth down the tree)
            #       TODO: Should we do this? Not sure the chances of city and
            #       state sharing the same name but New York, New York has
            #       already bite us.
            # if it doesn't then create it
            # continue until reach bottom node
            query = 'MATCH (a:Location {object_uuid: "%s"})-' \
                    '[:ENCOMPASSES*..]->(b:Location {name: "%s"}) RETURN b' % (
                        parent_node.object_uuid, name)
            res, _ = db.cypher_query(query)
            if not res.one:
                child_node = Location(name=name).save()
                parent_node.encompasses.connect(child_node)
                child_node.encompassed_by.connect(parent_node)
                parent_node = child_node
            else:
                parent_node = Location.inflate(res.one)

    return parent_node


def connect_related_element(location, element_id):
    # This could be generalized to manage other nodes we want to link to a
    # location but since we only do questions right now, simplifying it.
    from sb_questions.neo_models import Question
    query = 'MATCH (a:Question {external_location_id: %s}) RETURN a' % (
        element_id)
    res, _ = db.cypher_query(query)
    if not res.one:
        raise KeyError("Could not find Question yet")
    connection_node = Question.inflate(res.one)
    connection_node.connect(location)

    return connection_node
