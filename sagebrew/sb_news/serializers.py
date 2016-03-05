from django.utils.text import slugify
from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse

from sb_base.serializers import VotableContentSerializer

from .neo_models import NewsArticle


class NewsArticleSerializer(VotableContentSerializer):
    provider = serializers.ChoiceField(choices=[
        ('sb_crawler', "Sagebrew Crawler"), ('webhose', "Webhose.io"),
        ('alchemyapi', 'IBM Alchemy API')
    ])
    external_id = serializers.UUIDField()
    url = serializers.URLField()
    summary = serializers.CharField(read_only=True)
    site_full = serializers.CharField()
    site_section = serializers.CharField()
    section_title = serializers.CharField()
    title = serializers.CharField()
    title_full = serializers.CharField()
    highlight_title = serializers.CharField()
    highlight_text = serializers.CharField()
    language = serializers.ChoiceField(choices=settings.LANGUAGES)
    published = serializers.DateTimeField()
    replies_count = serializers.IntegerField()
    participants_count = serializers.IntegerField()
    site_type = serializers.CharField()
    country = serializers.ChoiceField(choices=settings.COUNTRIES)
    spam_score = serializers.FloatField()
    main_image = serializers.URLField()
    performance_score = serializers.IntegerField(min_value=0, max_value=10)
    crawled = serializers.DateTimeField()
    external_links = serializers.ListField(child=serializers.URLField())
    persons = serializers.ListField(child=serializers.CharField())
    locations = serializers.ListField(child=serializers.CharField())
    organizations = serializers.ListField(child=serializers.CharField())
    author = serializers.CharField()
    # Owner Username is defined in the parent class but not needed here
    owner_username = serializers.HiddenField(default=None)
    profile = serializers.HiddenField(default=None)

    def create(self, validated_data):
        instance = NewsArticle(**validated_data).save()
        return instance

    def update(self, instance, validated_data):
        return instance

    def get_type(self, obj):
        return "news_article"

    def get_href(self, obj):
        return reverse('news-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=self.context.get('request', None))

    def get_url(self, obj):
        return reverse('news',
                       kwargs={'object_uuid': obj.object_uuid,
                               'slug': slugify(obj.title)},
                       request=self.context.get('request', None))
