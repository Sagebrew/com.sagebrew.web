from api.serializers import SBSerializer


class OrderSerializer(SBSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass