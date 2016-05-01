import pytz
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError

from neomodel import db

from api.utils import generate_summary, cleanup_title, only_roman_chars
from sb_uploads.serializers import UploadSerializer
from sb_base.serializers import VotableContentSerializer

from .neo_models import NewsArticle


class NewsArticleSerializer(VotableContentSerializer):
    provider = serializers.ChoiceField(choices=[
        ('sb_crawler', "Sagebrew Crawler"), ('webhose', "Webhose.io"),
        ('alchemyapi', 'IBM Alchemy API')
    ])
    external_id = serializers.CharField()
    url = serializers.URLField()
    summary = serializers.CharField(read_only=True)
    site_full = serializers.CharField()
    site_section = serializers.CharField(required=False, allow_blank=True)
    section_title = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    title_full = serializers.CharField(required=False)
    highlight_title = serializers.CharField(allow_blank=True, required=False)
    highlight_text = serializers.CharField(allow_blank=True, required=False)
    language = serializers.ChoiceField(choices=settings.LANGUAGES)
    published = serializers.DateTimeField()
    replies_count = serializers.IntegerField(required=False)
    participants_count = serializers.IntegerField(required=False)
    site_type = serializers.CharField(required=False)
    country = serializers.ChoiceField(choices=settings.COUNTRIES)
    spam_score = serializers.FloatField()
    image = serializers.URLField()
    performance_score = serializers.IntegerField(min_value=0, max_value=10)
    crawled = serializers.DateTimeField()
    external_links = serializers.ListField(child=serializers.URLField(),
                                           required=False)
    persons = serializers.ListField(child=serializers.CharField(),
                                    required=False)
    locations = serializers.ListField(child=serializers.CharField(),
                                      required=False)
    organizations = serializers.ListField(child=serializers.CharField(),
                                          required=False)
    author = serializers.CharField(allow_blank=True, required=False)
    # Owner Username is defined in the parent class but not needed here
    owner_username = serializers.HiddenField(default=None)
    profile = serializers.HiddenField(default=None)

    def validate_external_id(self, value):
        query = 'MATCH (news:NewsArticle {external_id: "%s"}) ' \
                'RETURN news' % value
        res, _ = db.cypher_query(query)
        if res.one:
            raise ValidationError("This field must be unique")
        return value

    def validate_title(self, value):
        if not only_roman_chars(value):
            raise ValidationError("Can only have roman characters")
        # Clean up the title
        value = cleanup_title(value)
        # Check if title is in our excluded list or close to it
        for excluded_article in settings.DEFAULT_EXCLUDE_ARTICLES:
            # If the title has something similar to an article
            # we don't want to include, remove it
            # Not a list comprehension to ease readability. Not a
            # huge issue since this is normally called in a task.
            if SequenceMatcher(
                    a=excluded_article.lower(), b=value.lower()).ratio() > .70:
                raise ValidationError("Contains content that is "
                                      "not allowed")
        # Check if title already exists
        query = 'MATCH (news:NewsArticle {title: "%s"}) ' \
                'RETURN news' % value
        res, _ = db.cypher_query(query)
        if res.one is not None:
            raise ValidationError("This field must be unique")
        return value

    def validate_content(self, value):
        skip = 0
        summary = generate_summary(value)
        then = (datetime.now(pytz.utc) - timedelta(days=20)).strftime("%s")
        if summary.strip() == "" or summary is None:
            raise ValidationError("Could not produce a summary from the site")
        while True:
            query = 'MATCH (news:NewsArticle) WHERE news.created > %s ' \
                    'RETURN news ' \
                    'SKIP %s LIMIT 25' % (then, skip)
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for row in res:
                content_closeness = SequenceMatcher(
                    a=row[0]['content'], b=value).ratio()
                if content_closeness > 0.65:
                    raise ValidationError("Too close to another article")
                summary_closeness = SequenceMatcher(
                    a=row[0]['summary'], b=summary).ratio()
                if summary_closeness > 0.8:  # pragma: no cover
                    # Not requiring coverage here since summary is auto
                    # generated and in most instances content will be flagged
                    # before hand. - Devon Bleibtrey
                    raise ValidationError(
                        "Generated summary is too close to another article")
        return value

    def validate_image(self, value):
        serializer = UploadSerializer(
            data={"url": value},
            context={'request': self.context.get('request', None),
                     'folder': settings.AWS_UPLOAD_IMAGE_FOLDER_NAME,
                     'verify_unique': True,
                     'check_hamming': {'distance': 11, "time_frame": 15}})
        serializer.is_valid(raise_exception=True)
        return serializer

    def validate_url(self, value):
        # Using for loop instead of list comprehension for readability.
        for site in settings.EXPLICIT_SITES:
            if site in value:
                raise ValidationError("Explicit content found")
        for site in settings.UNSUPPORTED_UPLOAD_SITES:
            if site in value:
                raise ValidationError("Site not currently supported")
        query = 'MATCH (news:NewsArticle {url: "%s"}) ' \
                'RETURN news' % value
        res, _ = db.cypher_query(query)
        if res.one is not None:
            raise ValidationError("This field must be unique")
        return value

    def validate_site_full(self, value):
        for site in settings.UNSUPPORTED_UPLOAD_SITES:
            if site in value:
                raise ValidationError("Site not currently supported")

    def create(self, validated_data):
        validated_data['summary'] = generate_summary(
            validated_data.get('content'))
        # Wait till here to save the serializer so that we ensure all the other
        # validation checks pass before storing the data in the db
        upload = validated_data.get('image').save()
        validated_data['image'] = upload.url
        instance = NewsArticle(**validated_data).save()
        instance.images.connect(upload)
        return instance

    def get_type(self, obj):
        return "news_article"

    def get_href(self, obj):
        return reverse('news-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=self.context.get('request', None))
