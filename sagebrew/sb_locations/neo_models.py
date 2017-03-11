from neomodel import (db, StringProperty, RelationshipTo)

from sagebrew.api.neo_models import SBObject


class Location(SBObject):
    name = StringProperty(index=True)
    # Valid Sectors:
    #     state_upper - State Senator Districts
    #     state_lower - State House Representative Districts
    #     federal - U.S. Federal Districts (House of Reps)
    #     local - Everything else :)
    sector = StringProperty(default=None)
    geo_data = StringProperty(default=None)

    encompasses = RelationshipTo('sagebrew.sb_locations.neo_models.Location',
                                 'ENCOMPASSES')
    encompassed_by = RelationshipTo('sagebrew.sb_locations.neo_models.Location',
                                    'ENCOMPASSED_BY')
    # Questions
    # Access Questions that are related to this location through:
    # Neomodel: focus_location Cypher: FOCUSED_ON

    # Mission
    # Access Missions that are related to this location through:
    # Neomodel: location Cypher: WITHIN

    # optimizations
    # TODO these might be best moved to the Question or maybe lat, long to since
    # we only need to create the marker on the display page
    # Allows us to determine which service to query with the id for additional
    # info
    # valid values: smarty_streets, google_maps
    created_by = StringProperty(default="smarty_streets")
    # ID provided by a third party representing the ID that should be used
    # when querying their service.
    external_id = StringProperty(default=None, index=True)

    @classmethod
    def get_encompasses(cls, object_uuid):
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSES]->(e:`Location`) RETURN e.object_uuid' % (
                    object_uuid)
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def get_encompassed_by(cls, object_uuid):
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSED_BY]->(e:`Location`) RETURN e.object_uuid' % (
                    object_uuid)
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def get_single_encompassed_by(cls, object_uuid):
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSED_BY]->(e:`Location`) RETURN e.name' % (
                    object_uuid)
        res, _ = db.cypher_query(query)
        return res.one

    @classmethod
    def get_positions(cls, object_uuid):
        query = 'MATCH (l:`Location` {object_uuid: "%s"})-' \
                '[:POSITIONS_AVAILABLE]->(p:`Position`) RETURN ' \
                'p.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]
