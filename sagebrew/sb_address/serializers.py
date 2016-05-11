import us

from rest_framework import serializers
from rest_framework.reverse import reverse


from api.serializers import SBSerializer
from api.utils import spawn_task, gather_request_data

from .neo_models import Address
from .tasks import update_address_location


class AddressSerializer(SBSerializer):
    object_uuid = serializers.CharField(read_only=True)
    href = serializers.SerializerMethodField()
    street = serializers.CharField(max_length=128)
    street_additional = serializers.CharField(required=False, allow_blank=True,
                                              allow_null=True, max_length=128)
    city = serializers.CharField(max_length=150)
    state = serializers.CharField(max_length=50)
    postal_code = serializers.CharField(max_length=15)
    country = serializers.CharField(allow_null=True, required=False)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    congressional_district = serializers.IntegerField()
    validated = serializers.BooleanField(required=False)

    def create(self, validated_data):
        validated_data['state'] = us.states.lookup(
            validated_data['state']).name
        if not validated_data.get('country', False):
            validated_data['country'] = "USA"
        address = Address(**validated_data).save()
        address.set_encompassing()
        return address

    def update(self, instance, validated_data):
        instance.street = validated_data.get('street', instance.street)
        instance.street_additional = validated_data.get(
            'street_additional', instance.street_additional)
        instance.city = validated_data.get("city", instance.city)
        instance.state = us.states.lookup(
            validated_data.get("state", instance.state)).name
        instance.postal_code = validated_data.get("postal_code",
                                                  instance.postal_code)
        instance.country = validated_data.get("country", instance.country)
        instance.congressional_district = validated_data.get(
            "congressional_district", instance.congressional_district)
        instance.latitude = validated_data.get("latitude", instance.latitude)
        instance.longitude = validated_data.get("longitude",
                                                instance.longitude)
        instance.save()
        spawn_task(task_func=update_address_location,
                   task_param={"object_uuid": instance.object_uuid})
        return instance

    def get_href(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse(
            "address-detail", kwargs={'object_uuid': obj.object_uuid},
            request=request)


class AddressExportSerializer(serializers.Serializer):
    street = serializers.CharField(max_length=125)
    street_additional = serializers.CharField(required=False, allow_blank=True,
                                              allow_null=True, max_length=125)
    city = serializers.CharField(max_length=150)
    state = serializers.CharField(max_length=50)
    postal_code = serializers.CharField(max_length=15)
    country = serializers.CharField(allow_null=True, required=False)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    congressional_district = serializers.IntegerField()
