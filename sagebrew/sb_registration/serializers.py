from rest_framework import serializers

from sb_base.serializers import TitledContentSerializer

from .neo_models import OnboardingTask


class OnboardingTaskSerializer(TitledContentSerializer):
    title = serializers.CharField()
    content = serializers.CharField()
    image_url = serializers.CharField(required=False, allow_null=True)
    icon = serializers.CharField(required=False, allow_null=True)
    completed = serializers.BooleanField(default=False)
    completed_title = serializers.CharField()
    priority = serializers.IntegerField()
    url = serializers.URLField()
    can_flag = serializers.HiddenField(default=None)
    can_comment = serializers.HiddenField(default=None)
    can_upvote = serializers.HiddenField(default=None)
    can_downvote = serializers.HiddenField(default=None)

    def create(self, validated_data):
        from logging import getLogger
        logger = getLogger("loggly_logs")
        logger.critical(validated_data)
        instance = OnboardingTask(**validated_data).save()
        return instance

    def update(self, instance, validated_data):
        instance.completed = validated_data('completed')
        instance.save()
        return instance
