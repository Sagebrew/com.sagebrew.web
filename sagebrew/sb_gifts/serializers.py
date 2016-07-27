from rest_framework import serializers

from api.serializers import SBSerializer
from sb_missions.serializers import MissionSerializer

from .neo_models import Giftlist, Product


class GiftlistSerializer(SBSerializer):
    public = serializers.BooleanField(required=False)

    mission = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        current_ids = instance.get_product_vendor_ids()
        new_ids = validated_data.get("product_ids", [])
        for new_id in new_ids:
            if new_id not in current_ids:
                product = Product(vendor_id=new_id).save()
                product.giftlist.connect(instance)
        
        return instance.save()

    def get_mission(self, obj):
        return MissionSerializer(obj.get_mission()).data

    def get_products(self, obj):
        return [ProductSerializer(product).data
                for product in obj.get_products()]


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
        return GiftlistSerializer(obj.get_giftlist()).data
