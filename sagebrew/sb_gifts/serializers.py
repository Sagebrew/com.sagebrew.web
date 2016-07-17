from rest_framework import serializers

from neomodel import db

from api.serializers import SBSerializer
from .neo_models import Giftlist, Product


class GiftlistSerializer(SBSerializer):
    public = serializers.BooleanField(required=False)

    mission = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def get_mission(self, obj):
        pass

    def get_products(self, obj):
        pass


class ProductSerializer(SBSerializer):
    vendor_id = serializers.CharField(required=False)
    vendor_name = serializers.CharField(required=True)
    purchased = serializers.BooleanField(required=False)

    giftlist = serializers.SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def get_giftlist(self, obj):
        pass
