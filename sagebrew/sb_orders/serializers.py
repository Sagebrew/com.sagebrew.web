import stripe
from amazon.api import AmazonAPI

from django.conf import settings
from django.template import Context
from django.template.loader import get_template

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import chunk_list, gather_request_data
from api.serializers import SBSerializer
from sb_base.serializers import IntercomMessageSerializer
from plebs.neo_models import Pleb
from sb_gifts.neo_models import Product
from sb_gifts.serializers import ProductSerializer

from .neo_models import Order


class OrderSerializer(SBSerializer):
    # Denotes total price of the order stored as an integer with the last
    # two digits denoting cents
    # This price is the price calculated at time of checkout and potentially
    # could be different if Amazon has changed their pricing
    total = serializers.IntegerField(required=False)

    # List of products to be added to the order
    # Only used upon creation
    product_ids = serializers.ListField(required=False)

    owner_username = serializers.CharField(required=False)

    payment_method = serializers.CharField(required=False, write_only=True,
                                           allow_null=True)

    placed = serializers.DateTimeField(required=False)
    completed = serializers.BooleanField(required=False)
    paid = serializers.BooleanField(required=False)

    products = serializers.SerializerMethodField()
    mission = serializers.SerializerMethodField()

    def validate_total(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cannot be $0 or less")
        return value

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        product_ids = validated_data.get('product_ids', [])
        mission = validated_data.get('mission', None)
        total = validated_data.get('total', 0)
        owner = Pleb.get(request.user.username)
        order = Order(total=total, owner_username=owner.username).save()
        order.owner.connect(owner)
        order.mission.connect(mission)
        for product_id in product_ids:
            product = Product.nodes.get(object_uuid=product_id)
            product.orders.connect(order)

        return order

    def update(self, instance, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        mission = validated_data.pop('mission', None)
        quest = validated_data.pop('quest', None)
        payment_method = validated_data.pop('payment_method', None)

        donor = Pleb.get(instance.owner_username)
        quest_desc = quest.title \
            if quest.title else "%s %s" % (quest.first_name, quest.last_name)
        mission_desc = mission.get_mission_title()
        description = "Gift purchase to %s's mission for %s" % (quest_desc,
                                                                mission_desc)
        payment_method = payment_method if payment_method is not None \
            else donor.stripe_default_card_id
        stripe_res = stripe.Charge.create(
            customer=donor.stripe_customer_id,
            amount=instance.total,
            currency="usd",
            description=description,
            receipt_email=donor.email,
            source=payment_method
        )
        instance.stripe_charge_id = stripe_res['id']
        instance.paid = True
        instance.save()

        message_data = {
            'message_type': 'email',
            'subject': 'New Gift',
            'body': get_template('orders/email/new_order.html').render(
                Context({
                    'first_name': quest.first_name,
                    'mission_title': mission_desc,
                    "donor_first_name": donor.first_name,
                    "donor_last_name": donor.last_name,
                })),
            'template': "personal",
            'from_user': {
                'type': "admin",
                'id': settings.INTERCOM_ADMIN_ID_DEVON
            },
            'to_user': {
                'type': "user",
                'user_id': quest.owner_username
            }
        }
        serializer = IntercomMessageSerializer(data=message_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return instance

    def get_products(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        serialized_products = [ProductSerializer(product).data
                               for product in obj.get_products()]
        if expand == 'true':
            vendor_ids = [product['vendor_id']
                          for product in serialized_products]
            amazon = AmazonAPI("AKIAI5PAWWJNUQPPXL3Q",
                               "/XylsuBQopHlYC63+ZBjZ9HqEPmPHsH/9pMOPRjR",
                               "sagebrew-20")
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

    def get_mission(self, obj):
        from sb_missions.serializers import MissionSerializer
        mission = obj.get_mission()
        if mission:
            return MissionSerializer(obj.get_mission()).data
        return None
