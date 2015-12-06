from unidecode import unidecode

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
    Unable to get the external id for all of the components as google only
    gives us the external id of the leaf node.
    :param places:
    :param external_id:
    :return:
    """
    structure = verify_structure(break_out_structure(places), external_id)
    return create_tree(structure, external_id)


def google_maps_query(external_id):
    url = "https://maps.googleapis.com/maps/api/" \
          "place/details/json?placeid=%s&key=%s" % (
              external_id, settings.GOOGLE_MAPS_API_SERVER)
    response = get(url, headers={
        "content-type": "application/json"})
    return break_out_structure(response.json()['result']['address_components'])


def break_out_structure(places):
    us_variants = ['United States', 'USA', 'US']
    country = None
    admin_area_1 = None
    locality = None
    for place in places:
        if 'country' in place['types']:
            country = place
            if country['long_name'] in us_variants:
                country['long_name'] = "United States of America"
        elif 'administrative_area_level_1' in place['types']:
            admin_area_1 = place
        # Taking out county for time being as with the current query it will
        # cause duplicate cities
        # elif 'administrative_area_level_2' in place['types']:
        #    admin_area_2 = place
        elif ('administrative_area_level_3' in place['types'] or
                'locality' in place['types']):
            locality = place

    return [country, admin_area_1, locality]


def verify_structure(structure, external_id, verify=True):
    for idx, place in enumerate(structure):
        if place is None:
            # check to make sure we've actually hit the end and aren't just
            # missing an intermediate location due to Google not returning it
            for r_idx, remaining in enumerate(structure[idx + 1:]):
                # If we aren't at the last node yet go ask Google again for
                # the full structure and restart the function with a flag that
                # stops us from constantly asking google
                if remaining is not None and verify is True:
                    return verify_structure(google_maps_query(external_id),
                                            external_id, False)

    # We're actually at the end. We should remove all the remaining Nones
    return [x for x in structure if x is not None]


def create_tree(structure, external_id):
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
        try:
            name = unidecode(unicode(element['long_name']))
        except TypeError:
            # Handles cases where the name is already in unicode format
            name = unidecode(element['long_name'])
        if idx == 0:
            # Could craft out a CREATE UNIQUE potentially but rather create
            # node with neomodel to get UUID and defaults set properly
            query = 'MATCH (a:Location {name: "%s"}) RETURN a' % name
            res, _ = db.cypher_query(query)
            if not res.one:
                parent_node = Location(
                    name=name, created_by="google_maps",
                    sector="federal").save()
            else:
                parent_node = Location.inflate(res.one)
        else:
            # Otherwise take parent and see if it has any children with name
            #       (Check if any children at any depth down the tree)
            #       TODO: Should we do this? Not sure the chances of city and
            #       state sharing the same name but New York, New York has
            #       already bit us.
            # if it doesn't then create it
            # continue until reach bottom node
            query = 'MATCH (a:Location {object_uuid: "%s"})-' \
                    '[:ENCOMPASSES]->(b:Location {name: "%s"}) RETURN b' % (
                        parent_node.object_uuid, name)
            res, _ = db.cypher_query(query)

            if not res.one:
                if 'locality' in element['types']:
                    sector = "local"
                    external_holder = external_id
                else:
                    sector = None
                    external_holder = None
                child_node = Location(
                    name=name, created_by="google_maps", sector=sector,
                    external_id=external_holder).save()
                parent_node.encompasses.connect(child_node)
                child_node.encompassed_by.connect(parent_node)
                parent_node = child_node
            else:
                parent_node = Location.inflate(res.one)
                if 'locality' in element['types']:
                    parent_node.sector = "local"
                    parent_node.external_id = external_id
                    parent_node.created_by = "google_maps"
                    parent_node.save()

    return parent_node


def connect_related_element(location, element_id):
    # This could be generalized to manage other nodes we want to link to a
    # location but since we only do questions right now, simplifying it.
    from sb_questions.neo_models import Question
    query = 'MATCH (a:Question {external_location_id: "%s"}) RETURN a' % (
        element_id)
    res, _ = db.cypher_query(query)
    if not res.one:
        raise KeyError("Could not find Question yet")
    connection_node = Question.inflate(res.one)
    connection_node.focus_location.connect(location)

    return connection_node


def get_positions(identifier, filter_param="", lookup="name", distinct=False,
                  property_name=""):
    federal_positions = ""
    distinct_string = ""
    non_external_id = ""
    if filter_param == "state":
        constructed_filter = 'WHERE p.level="state_upper" ' \
                             'OR p.level="state_lower"'
    elif filter_param == '' or filter_param is None or filter_param == "local":
        constructed_filter = ''
    else:
        constructed_filter = 'WHERE p.level="%s"' % filter_param

    if distinct:
        distinct_string = "DISTINCT"

    if filter_param == "federal":
        federal_positions = ' UNION MATCH (:Location ' \
                            '{name: "United States of America"})-' \
                            '[:POSITIONS_AVAILABLE]->(p:Position) ' \
                            'RETURN %s p%s' % (distinct_string, property_name)
    if lookup != "external_id":
        # If we don't have an external id we'll want to ensure the location
        # is kept within the USA since that's the only area we have positions
        # TODO: May be able to remove this
        non_external_id = '(:Location {name: "United States of America"})-' \
                          '[:ENCOMPASSES]->'

    if filter_param != "local":
        query = 'MATCH %s(l:Location {%s: "%s"})-[:ENCOMPASSES*..]->' \
                '(l2:Location)-[:POSITIONS_AVAILABLE]->(p:Position) %s ' \
                'RETURN %s p%s UNION MATCH (:Location ' \
                '{name: "United States of America"})-' \
                '[:ENCOMPASSES]->(l:Location {%s: "%s"})' \
                '-[:POSITIONS_AVAILABLE]->(p:Position) %s RETURN %s p%s%s' \
                % (non_external_id, lookup, identifier, constructed_filter,
                   distinct_string, property_name, lookup, identifier,
                   constructed_filter, distinct_string, property_name,
                   federal_positions)
    else:
        query = 'MATCH (l:Location {external_id: "%s"})-' \
                '[:POSITIONS_AVAILABLE]->(p:Position) RETURN %s p%s' % (
                    identifier, distinct_string, property_name)
    res, _ = db.cypher_query(query)
    if not res.one:
        return []
    return res


def get_districts(identifier, filter_param="", lookup="name", distinct=False,
                  property_name=""):
    if filter_param == "state":
        constructed_filter = 'WHERE l.sector="state_upper" ' \
                             'OR l.sector="state_lower"'
    elif filter_param == '':
        constructed_filter = ''
    else:
        constructed_filter = 'WHERE l.sector="%s"' % filter_param

    if distinct:
        distinct_string = "DISTINCT"
    else:
        distinct_string = ""
    query = 'MATCH (l2:Location {%s: "%s"})-[:ENCOMPASSES*..]->' \
            '(l:Location) %s RETURN %s l%s ORDER BY l.name' % (
                lookup, identifier, constructed_filter, distinct_string,
                property_name)
    res, _ = db.cypher_query(query)
    if not res.one:
        return []
    return res
