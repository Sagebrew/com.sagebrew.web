from django.utils.text import slugify

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.serializers import SBSerializer


class TagSerializer(SBSerializer):
    name = serializers.CharField(max_length=140)
    href = serializers.SerializerMethodField()

    def get_href(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return None
        return reverse('tag-detail',
                       kwargs={'name': slugify(obj.name)}, request=request)
