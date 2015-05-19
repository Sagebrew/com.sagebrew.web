from rest_framework import serializers


class CountrySerializer(serializers.Serializer):
    name = serializers.CharField()

    locations = serializers.SerializerMethodField()
    states = serializers.SerializerMethodField()
    districts = serializers.SerializerMethodField()

    def get_locations(self, obj):
        pass

    def get_states(self, obj):
        pass

    def get_districts(self, obj):
        pass


class LocationSerializer(serializers.Serializer):
    geo_data = serializers.CharField()

    states = serializers.SerializerMethodField()

    def get_states(self, obj):
        pass


class StateSerializer(serializers.Serializer):
    name = serializers.CharField()

    districts = serializers.SerializerMethodField()

    def get_districts(self, obj):
        pass


class DistrictSerializer(serializers.Serializer):
    number = serializers.IntegerField()

    state = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    positions_available = serializers.SerializerMethodField()

    def get_state(self, obj):
        pass

    def get_addresses(self, obj):
        pass

    def get_positions_available(self, obj):
        pass
