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
        encompasses = Location.get_encompasses(obj.object_uuid)
        if relations == 'hyperlink':
            return [reverse('location-detail', kwargs={'object_uuid': row[0]},
                            request=request) for row in encompasses]
        return encompasses

    def get_encompassed_by(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        encompassed_by = Location.get_encompassed_by(obj.object_uuid)
        if relations == 'hyperlink':
            return [reverse('location-detail', kwargs={'object_uuid': row[0]},
                            request=request) for row in encompassed_by]
        return encompassed_by

    def get_positions(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        positions = Location.get_positions(obj.object_uuid)
        if relations == 'hyperlink':
            return [reverse('position-detail',
                            kwargs={'object_uuid': row[0]}, request=request)
                    for row in positions]
        return positions

    def get_geo_data(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        if obj.geo_data is None:
            return False
        if expand == 'true':
            return loads(obj.geo_data)
        return True
