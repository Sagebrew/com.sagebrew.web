from rest_framework import serializers

from api.serializers import SBSerializer


class NotificationSerializer(SBSerializer):
    seen = serializers.BooleanField(read_only=True)
    time_sent = serializers.DateTimeField(read_only=True)
    time_seen = serializers.DateTimeField(read_only=True)
    about = serializers.CharField(read_only=True)
    sent = serializers.BooleanField(read_only=True)
    url = serializers.CharField(read_only=True)
    action_name = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # Creation is done in a task based on internal attributes and objects
        # There isn't any user input used when generating the notification so
        # we don't need to run the info through the serializer to save it
        pass

    def update(self, instance, validated_data):
        # We don't actually update a notification based on user input
        # We just mark it as seen or not seen. We won't mark it as seen
        # based on a given hit of the API but rather when the front end
        # indicates that a user has had the chance to view the given
        # notification
        pass
