from rest_framework import serializers

from api.serializers import SBSerializer
from sb_gifts.neo_models import Product

from .neo_models import Order


class OrderSerializer(SBSerializer):
    # Denotes total price of the order stored as an integer with the last
    # two digits denoting cents
    # This price is the price calculated at time of checkout and potentially
    # could be different if Amazon has changed their pricing
    total = serializers.IntegerField()

    # List of products to be added to the order
    # Only used upon creation
    product_ids = serializers.ListField(required=False)

    placed = serializers.DateTimeField(required=False)
    completed = serializers.BooleanField(required=False)

    def create(self, validated_data):
        request = self.context['request']
        product_ids = validated_data.get('product_ids', [])
        total = validated_data.get('total', 0)
        if total <= 0:
            raise serializers.ValidationError("Total cannot be $0 or less")
        order = Order(total=total).save()
        for product_id in product_ids:
            product = Product.nodes.get(object_uuid=product_id)
            product.orders.connect(order)

        # TODO stripe charge

        return order

    def update(self, instance, validated_data):
        pass