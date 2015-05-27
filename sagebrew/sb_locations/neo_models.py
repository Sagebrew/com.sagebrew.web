from neomodel import (db, StringProperty, RelationshipTo)

from api.neo_models import SBObject


class Location(SBObject):
    name = StringProperty()
    geo_data = StringProperty(default=None)

    encompasses = RelationshipTo('sb_locations.neo_models.Location',
                                 'ENCOMPASSES')
    encompassed_by = RelationshipTo('sb_locations.neo_models.Location',
                                    'ENCOMPASSED_BY')
    positions = RelationshipTo('sb_campaigns.neo_models.Position',
                               'POSITIONS_AVAILABLE')

    @classmethod
    def get_encompasses(cls, object_uuid):
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSES]->(e:`Location`) RETURN e.object_uuid' % \
                (object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return res
        return [row[0] for row in res]

    @classmethod
    def get_encompassed_by(cls, object_uuid):
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSED_BY]->(e:`Location`) RETURN e.object_uuid' \
                % (object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return res
        return [row[0] for row in res]

    @classmethod
    def get_positions(cls, object_uuid):
        query = 'MATCH (l:`Location` {object_uuid: "%s"})-' \
                '[:POSITIONS_AVAILABLE]->(p:`Position`) RETURN p.object_uuid' \
                % (object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return res
        return [row[0] for row in res]
