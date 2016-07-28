from amazon.api import AmazonAPI
from rest_framework import serializers

from api.serializers import SBSerializer
from sb_missions.serializers import MissionSerializer

from .neo_models import Giftlist, Product


class GiftlistSerializer(SBSerializer):
    public = serializers.BooleanField(required=False)
    product_ids = serializers.ListField(required=False)

    mission = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    def create(self, validated_data):
        # We don't allow users to create additional Giftlists yet as each
        # Mission will only have one, which we create via management command,
        # for ease of management (both of us and them) upon initial
        # release of the feature.
        pass

    def update(self, instance, validated_data):
        '''
        Add Products to the list or remove existing products.

        You MUST pass the full list of IDs or else any missing
        IDs will be removed from the list.

        Any Products not attached to the Giftlist will be created and attached.

        :param instance:
        :param validated_data:
        :return:
        '''
        current_ids = instance.get_product_vendor_ids()
        # call set() here to ensure no duplicates
        new_ids = list(set(validated_data.get("product_ids", [])))
        for new_id in new_ids:
            if new_id not in current_ids:
                product = Product(vendor_id=new_id).save()
                product.giftlist.connect(instance)
        for old_id in current_ids:
            if old_id not in new_ids:
                product = instance.get_product(
                    vendor_id=old_id, vendor_name="amazon")
                product.giftlist.disconnect(instance)
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
    information = serializers.SerializerMethodField()

    def create(self, validated_data):
        # Currently we don't allow users to create Products.
        # May be implemented if people want to sell yard signs or
        # something in the future.
        pass

    def update(self, instance, validated_data):
        # Should not need to update products because the
        # ASIN(Amazon Standard Identification Number) should never change as
        # Amazon uses them to uniquely identify products as shown here:
        # http://docs.aws.amazon.com/AWSECommerceService/
        # latest/DG/ItemLookup.html#ItemLookup-resp
        pass

    def get_giftlist(self, obj):
        return obj.get_giftlist().object_uuid

    def get_information(self, obj):
        info = {}
        if obj.vendor_name == "amazon":
            # TODO move these strings into settings variables
            amazon = AmazonAPI("AKIAI5PAWWJNUQPPXL3Q",
                               "/XylsuBQopHlYC63+ZBjZ9HqEPmPHsH/9pMOPRjR",
                               "sagebrew-20")
            product = amazon.lookup(ItemId=obj.vendor_id)
            price, currency = product.price_and_currency
            info = {
                "title": product.title,
                "image": product.large_image_url,
                "price": price,
                "currency": currency,
                "asin": product.asin,
                "url": product.offer_url
            }
        return info
