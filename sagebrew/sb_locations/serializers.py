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
        request, expand, _, _, _ = gather_request_data(self.context)
        encompass_list = []
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSES]-(e:`Location`) RETURN e' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        for location in [Location.inflate(row[0]) for row in res]:
            if expand == 'true':
                encompass_list.append(reverse('location-detail',
                                      kwargs={"object_uuid":
                                                  location.object_uuid},
                                      request=request))
                continue
            encompass_list.append(location.object_uuid)
        return encompass_list

    def get_encompassed_by(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        encompass_list = []
        query = 'MATCH (n:`Location` {object_uuid: "%s"})-' \
                '[:ENCOMPASSED_BY]-(e:`Location`) RETURN e' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        for location in [Location.inflate(row[0]) for row in res]:
            if expand == 'true':
                encompass_list.append(reverse('location-detail',
                                      kwargs={"object_uuid":
                                                  location.object_uuid},
                                      request=request))
                continue
            encompass_list.append(location.object_uuid)
        return encompass_list

    def get_positions(self, obj):
        position_list = []
        request, expand, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (l:`Location` {object_uuid: "%s"})-' \
                '[:POSITIONS_AVAILABLE]-(p:`Position`) RETURN p' % \
                (obj.object_uuid)
        res, col = db.cypher_query(query)
        for position in [Position.inflate(row[0]) for row in res]:
            if expand == 'true':
                position_list.append(reverse('position-detail',
                                             kwargs={"object_uuid":
                                                         position.object_uuid},
                                             request=request))
                continue
            position_list.append(position.object_uuid)
        return position_list

    def get_geo_data(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        if obj.geo_data is None:
            return False
        if expand == 'true':
            return loads(obj.geo_data)
        return True
