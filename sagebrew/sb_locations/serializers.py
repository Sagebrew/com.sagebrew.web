from json import loads
from unidecode import unidecode

from rest_framework.reverse import reverse
from rest_framework import serializers

from neomodel.exception import DoesNotExist

from neomodel import db

from api.utils import gather_request_data, spawn_task
from api.serializers import SBSerializer

from .neo_models import Location
from .tasks import create_location_tree


class LocationSerializer(SBSerializer):
    name = serializers.CharField()
    sector = serializers.ChoiceField(choices=[
        ('state_upper', "State Upper"), ('state_lower', "State Lower"),
        ('federal', "Federal"), ('local', "Local")])
    encompasses = serializers.SerializerMethodField()
    encompassed_by = serializers.SerializerMethodField()
    positions = serializers.SerializerMethodField()
    geo_data = serializers.SerializerMethodField()
    external_id = serializers.CharField()

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


class LocationExternalIDSerializer(serializers.Serializer):
    place_id = serializers.CharField(max_length=120, required=True,
                                     write_only=True)

    def create(self, validated_data):
        query = 'MATCH (a:Location {external_id: "%s"}) RETURN a' % (
                validated_data.get('place_id'))
        res, _ = db.cypher_query(query)
        if res.one is None:
            spawn_task(task_func=create_location_tree, task_param={
                "external_id": validated_data.get('place_id')})
        return res


class LocationManagerSerializer(SBSerializer):
    name = serializers.CharField()
    geo_data = serializers.CharField(allow_null=True)
    encompassed_by_name = serializers.CharField(
        allow_blank=True, help_text="Enter the name of the encompassing area. "
                                    "This or uuid can be used but not both!",
        required=False)
    encompassed_by_uuid = serializers.CharField(
        allow_blank=True, help_text="Enter the UUID of the encompassing area. "
                                    "This or name can be used but not both!",
        required=False)

    def validate_name(self, value):
        # We need to escape quotes prior to passing the title to the query.
        # Otherwise the query will fail due to the string being terminated.
        temp_value = value
        temp_value = temp_value.replace('"', '\\"')
        temp_value = temp_value.replace("'", "\\'")
        try:
            temp_value = unidecode(unicode(temp_value, "utf-8"))
        except TypeError:
            # Handles cases where the name is already in unicode format
            temp_value = unidecode(temp_value)
        query = 'MATCH (l:Location {name: "%s"}) RETURN l' % temp_value
        res, _ = db.cypher_query(query)
        if res.one is not None:
            raise serializers.ValidationError(
                {"name": "Sorry looks like a Location with that Name "
                         "already Exists"})
        return value

    def create(self, validated_data):
        encompassed_by = None
        location_name = validated_data.pop('encompassed_by_name', '')
        location_id = validated_data.pop('encompassed_by_uuid', '')
        name = validated_data.get('name', '')
        try:
            name = unidecode(unicode(name, "utf-8"))
        except TypeError:
            # Handles cases where the name is already in unicode format
            name = unidecode(name)
        validated_data['name'] = name
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
