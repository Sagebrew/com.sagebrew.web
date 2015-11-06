from neomodel import db

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
    if country is not None:
        # First check if everything already exists
        query = 'MATCH (a:Location {name: %s})'
        return_string = " RETURN a"
        end_node = "a"
        if admin_area_1 is not None:
            query += "-[ENCOMPASSES]->(b:Location {name: %s})"
            return_string += ",b"
            end_node = "b"
        if admin_area_2 is not None:
            query += "-[ENCOMPASSES]->(c:Location {name: %s})"
            return_string += ",c"
            end_node = "c"
        if locality is not None:
            query += "-[ENCOMPASSES]->(d:Location {name: %s})"
            return_string += ",d"
            end_node = "d"
        query += return_string
        res, _ = db.cypher_query(query)
        if res.one:
            return Location.inflate(res[end_node])
        # If not figure out what doesn't
        country_node = get_or_create_country(country['long_name'])
        if admin_area_1 is not None:
            admin_area_1_node = get_or_create_area_1(
                country_node, admin_area_1['long_name'])
            if admin_area_2 is not None:
                admin_area_2_node = get_or_create_area_2(
                    country_node, admin_area_1_node, admin_area_2['long_name'])
        elif admin_area_2 is not None and admin_area_1 is None:
            # TODO Query google for admin area 2 to get area 1
            query = ""
            res, _ = db.cypher_query(query)
            admin_area_1_node = res['admin_area1']
            admin_area_2_node = res['admin_area2']


def get_or_create_country(country_name):
    query = "MATCH (a:Location {name: %s}) RETURN a" % country_name
    res, _ = db.cypher_query(query)
    if not res.one:
        country = Location(name=country_name).save()
    else:
        country = Location.inflate(res.one)
    return country


def get_or_create_area_1(parent_node, child_name):
    query = "MATCH (a:Location {name: %s})-" \
            "[:ENCOMPASSES]->(b:Location {name: %s}) RETURN b" % (
                parent_node.name, child_name)
    res, _ = db.cypher_query(query)
    if not res.one:
        admin_area_1_node = Location(name=child_name).save()
        admin_area_1_node.encompassed_by.connect(parent_node)
        parent_node.encompasses.connect(admin_area_1_node)
    else:
        admin_area_1_node = Location.inflate(res.one)
    return admin_area_1_node


def get_or_create_area_2(parent_node, child_node, sub_child_name):
    query = "MATCH (a:Location {name: %s})-" \
            "[:ENCOMPASSES]->(b:Location {name: %s})-" \
            "[:ENCOMPASSES]->(c:Location {name: %s}) RETURN c" % (
                parent_node.name, child_node.name, sub_child_name)
    res, _ = db.cypher_query(query)
    if not res.one:
        admin_area_2_node = Location(name=sub_child_name).save()
        admin_area_2_node.encompassed_by.connect(child_node)
        child_node.encompasses.connect(admin_area_2_node)
    else:
        admin_area_2_node = Location.inflate(res.one)
    return admin_area_2_node
