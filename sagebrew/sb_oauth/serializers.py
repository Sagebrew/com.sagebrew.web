from django.contrib.auth.models import User

from rest_framework import serializers
from oauth2_provider.generators import (generate_client_id,
                                        generate_client_secret)

from .models import SBApplication


class ApplicationSerializer(serializers.Serializer):
    client_id = serializers.CharField(read_only=True)
    user = serializers.HyperlinkedRelatedField(queryset=User.objects.all(),
                                               view_name="user-detail",
                                               lookup_field="username")
    redirect_uris = serializers.CharField(required=False)
    client_type = serializers.ChoiceField(required=True,
                                          choices=SBApplication.CLIENT_TYPES)
    authorization_grant_type = serializers.ChoiceField(
        required=True, choices=SBApplication.GRANT_TYPES)
    client_secret = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255, required=False)
    web_hook = serializers.URLField(required=True)
    reset_credentials = serializers.BooleanField(required=False,
                                                 write_only=True)

    def create(self, validated_data):
        validated_data["client_id"] = generate_client_id()
        validated_data["client_secret"] = generate_client_secret()
        return SBApplication.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.redirect_uris = validated_data.get(
            'redirect_uris', instance.redirect_uris)
        instance.name = validated_data.get('name', instance.name)
        instance.web_hook = validated_data.get('web_hook', instance.web_hook)
        if validated_data.get('reset_credentials', False) is True:
            instance.client_id = generate_client_id()
            instance.client_secret = generate_client_secret()
        instance.save()
        return instance
