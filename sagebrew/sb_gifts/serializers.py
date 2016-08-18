from django.conf import settings

from amazon.api import AmazonAPI
from rest_framework import serializers

from api.utils import chunk_list, gather_request_data
from api.serializers import SBSerializer
from sb_missions.serializers import MissionSerializer

from .neo_models import Product


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
        new_ids = validated_data.get("product_ids", [])
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

    def validate_product_ids(self, value):
        # remove duplicates from the list of product ids
        return list(set(value))

    def get_mission(self, obj):
        return MissionSerializer(obj.get_mission()).data

    def get_products(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        serialized_products = [ProductSerializer(product).data
                               for product in obj.get_products()]
        if expand == 'true': # pragma: no cover
            # Not covering this as we have no good way to mock a request to
            # the amazon api as they use request signatures. - Devon Bleibtrey
            vendor_ids = [product['vendor_id']
                          for product in serialized_products]
            amazon = AmazonAPI(settings.AMAZON_PROMOTION_API_KEY,
                               settings.AMAZON_PROMOTION_API_SECRET_KEY,
                               settings.AMAZON_ASSOCIATE_TAG)
            for sub_list in chunk_list(vendor_ids, 10):
                sub_ids = ",".join(sub_list)
                products = amazon.lookup(ItemId=sub_ids)
                if not hasattr(products, '__iter__'):
                    products = [products]
                for product in products:
                    match = next((l for l in serialized_products
                                  if l['vendor_id'] == product.asin), None)
                    if match is not None:
                        price, currency = product.price_and_currency
                        match['information'] = {
                            "title": product.title,
                            "image": product.large_image_url,
                            "price": price,
                            "currency": currency,
                            "asin": product.asin,
                            "url": product.offer_url
                        }
        return serialized_products


class ProductSerializer(SBSerializer):
    vendor_id = serializers.CharField(required=False)
    vendor_name = serializers.CharField(required=True)

    giftlist = serializers.SerializerMethodField()

    def create(self, validated_data):
        # Currently we don't allow users to create Products.
        # May be implemented if people want to sell yard signs or
        # something that they personally fund/create in the future.
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
