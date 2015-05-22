from json import loads

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import gather_request_data

from sb_campaigns.neo_models import Position

from .neo_models import Location


class LocationSerializer(serializers.Serializer):
    name = serializers.CharField()

    encompasses = serializers.SerializerMethodField()
    encompassed_by = serializers.SerializerMethodField()
    positions = serializers.SerializerMethodField()
    geo_data = serializers.SerializerMethodField()

    def get_encompasses(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        encompass_list = []
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSES]->(e:`Location`) RETURN e.object_uuid' % \
                (obj.object_uuid)
        res, col = db.cypher_query(query)
        if relations == 'hyperlink':
            for location in [row[0] for row in res]:
                encompass_list.append(reverse('location-detail',
                                      kwargs={"object_uuid":
                                                  location},
                                      request=request))
            return encompass_list
        return [row[0] for row in res]

    def get_encompassed_by(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        encompass_list = []
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSED_BY]->(e:`Location`) RETURN e.object_uuid' \
                % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if relations == 'hyperlink':
            for location in [row[0] for row in res]:
                encompass_list.append(reverse('location-detail',
                                      kwargs={"object_uuid":
                                                  location},
                                      request=request))
            return encompass_list
        return [row[0] for row in res]

    def get_positions(self, obj):
        position_list = []
        request, _, _, relations, _ = gather_request_data(self.context)
        query = 'MATCH (l:`Location` {object_uuid: "%s"})-' \
                '[:POSITIONS_AVAILABLE]->(p:`Position`) RETURN p.object_uuid' \
                % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if relations == 'hyperlink':
            for position in [row[0] for row in res]:
                position_list.append(reverse('position-detail',
                                             kwargs={"object_uuid":
                                                         position},
                                             request=request))
            return position_list
        return [row[0] for row in res]

    def get_geo_data(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        if obj.geo_data is None:
            return False
        if expand == 'true':
            return loads(obj.geo_data)
        return True
