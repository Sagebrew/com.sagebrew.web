from json import loads

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import DoesNotExist

from neomodel import db

from api.utils import gather_request_data
from api.serializers import SBSerializer

from .neo_models import Location


class LocationSerializer(SBSerializer):
    name = serializers.CharField()

    encompasses = serializers.SerializerMethodField()
    encompassed_by = serializers.SerializerMethodField()
    positions = serializers.SerializerMethodField()
    geo_data = serializers.SerializerMethodField()

    def get_encompasses(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        encompasses = Location.get_encompasses(obj.object_uuid)
        if relations == 'hyperlink':
            return [reverse('location-detail', kwargs={'object_uuid': row},
                            request=request) for row in encompasses]
        return encompasses

    def get_encompassed_by(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        encompassed_by = Location.get_encompassed_by(obj.object_uuid)
        if relations == 'hyperlink':
            return [reverse('location-detail', kwargs={'object_uuid': row},
                            request=request) for row in encompassed_by]
        return encompassed_by

    def get_positions(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        positions = Location.get_positions(obj.object_uuid)
        if relations == 'hyperlink':
            return [reverse('position-detail',
                            kwargs={'object_uuid': row}, request=request)
                    for row in positions]
        return positions

    def get_geo_data(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        if obj.geo_data is None:
            return False
        if expand == 'true':
            return loads(obj.geo_data)
        return True


class LocationManagerSerializer(SBSerializer):
    name = serializers.CharField()
    geo_data = serializers.CharField(allow_null=True)
    encompassed_by_name = serializers.CharField(
        allow_blank=True, help_text="Enter the name of the encompassing area. "
                                    "This or uuid can be used but not both!")
    encompassed_by_uuid = serializers.CharField(
        allow_blank=True, help_text="Enter the UUID of the encompassing area. "
                                    "This or name can be used but not both!")

    def validate_name(self, value):
        # We need to escape quotes prior to passing the title to the query.
        # Otherwise the query will fail due to the string being terminated.
        temp_value = value
        temp_value = temp_value.replace('"', '\\"')
        temp_value = temp_value.replace("'", "\\'")
        query = 'MATCH (l:Location {name: "%s"}) RETURN l' % temp_value
        res, _ = db.cypher_query(query)
        if res.one is not None:
            raise serializers.ValidationError("Sorry looks like a Location"
                                              " with that Name already Exists")
        return value

    def create(self, validated_data):
        encompassed_by = None
        location_name = validated_data.pop('encompassed_by_name', '')
        location_id = validated_data.pop('encompassed_by_uuid', '')
        try:
            encompassed_by = Location.nodes.get(name=location_name)
        except(Location.DoesNotExist, DoesNotExist):
            pass
        if encompassed_by is None:
            try:
                encompassed_by = Location.nodes.get(object_uuid=location_id)
            except(Location.DoesNotExist, DoesNotExist):
                pass
        location = Location(**validated_data).save()
        if encompassed_by is not None:
            location.encompassed_by.connect(encompassed_by)
            encompassed_by.encompasses.connect(location)

        return location
