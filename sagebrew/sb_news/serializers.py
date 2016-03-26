from difflib import SequenceMatcher
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from django.utils.text import slugify
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
    title_full = serializers.CharField()
    highlight_title = serializers.CharField(allow_blank=True, required=False)
    highlight_text = serializers.CharField(allow_blank=True, required=False)
    language = serializers.ChoiceField(choices=settings.LANGUAGES)
    published = serializers.DateTimeField()
    replies_count = serializers.IntegerField()
    participants_count = serializers.IntegerField()
    site_type = serializers.CharField()
    country = serializers.ChoiceField(choices=settings.COUNTRIES)
    spam_score = serializers.FloatField()
    image = serializers.URLField()
    performance_score = serializers.IntegerField(min_value=0, max_value=10)
    crawled = serializers.DateTimeField()
    external_links = serializers.ListField(child=serializers.URLField())
    persons = serializers.ListField(child=serializers.CharField())
    locations = serializers.ListField(child=serializers.CharField())
    organizations = serializers.ListField(child=serializers.CharField())
    author = serializers.CharField(allow_blank=True)
    # Owner Username is defined in the parent class but not needed here
    owner_username = serializers.HiddenField(default=None)
    profile = serializers.HiddenField(default=None)

    def validate(self, data):
        # Execute multiple fields here to reduce the for loops necessary and
        # queries if they were all done in their own fields.
        title = cleanup_title(data['title'])
        image = data['image']
        url = data['url']
        content = data['content']
        # Get news articles with close titles, exact titles, or
        # the same main
        query = """
                MATCH (news:NewsArticle)
                WHERE (news.title =~ "(?i).*%s.*" ) OR
                news.image = "%s"
                RETURN news""" % (title, image)
        res, _ = db.cypher_query(query)
        for row in res:
            # Check if they go to the same page
            current_url = urlparse(url)
            compare_url = urlparse(row[0]['url'])
            if current_url.path == compare_url.path \
                    and current_url.netloc == compare_url.netloc:
                raise ValidationError("URL must be unique")
            # Make sure we're not getting some explicit site through
            # the crawlers
            if [site for site in settings.EXPLICIT_SITES
                    if site in current_url.netloc]:
                raise ValidationError("Explicit content found")
            # Check how close the titles are together
            title_closeness = SequenceMatcher(
                a=row[0]['title'], b=title).ratio()
            # Check how close the content is to each other
            content_closeness = SequenceMatcher(
                a=row[0]['content'], b=content).ratio()
            if title_closeness > 0.83 or content_closeness > 0.85:
                raise ValidationError("Title too close to existing content")
            # See if they share an image
            if row[0]['image'] == image:
                # If they share the same image could still be
                # different stories but since we don't want to show
                # the same image twice on a feed lets be more strict
                # on how different they need to be
                if title_closeness > 0.65 or content_closeness > 0.65:
                    raise ValidationError("Title too close to existing content")
        return data

    def validate_external_id(self, value):
        query = 'MATCH (news:NewsArticle {external_id: "%s"}) ' \
                'RETURN news' % value
        res, _ = db.cypher_query(query)
        if res.one:
            raise ValidationError("This field must be unique")
        return value

    def validate_title(self, value):
        if not only_roman_chars(value):
            raise ValidationError("Title can only have roman characters")
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
                raise ValidationError("Title contains content that is "
                                      "not allowed")
        # Check if title already exists
        query = 'MATCH (news:NewsArticle) ' \
                'WHERE news.title = "%s" RETURN news' % value
        res, _ = db.cypher_query(query)
        if res.one is not None:
            raise ValidationError("This field must be unique")
        return value

    def validate_content(self, value):
        skip = 0
        summary = generate_summary(value)
        if summary.strip() == "" or summary is None:
            raise ValidationError("Could not produce a summary from the site")
        while True:
            query = 'MATCH (news:NewsArticle) RETURN news ' \
                    'SKIP %s LIMIT 25' % skip
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
                    a=row[0]['summary'], b=summary)
                if summary_closeness > 0.65:
                    raise ValidationError(
                        "Generated summary is too close to another article")
        return value

    def validate_image(self, value):
        if value == "" or value is None:
            raise ValidationError("Invalid URL")
        serializer = UploadSerializer(
            data={"url": value},
            context={'request': self.context.get('request', None),
                     'folder': settings.AWS_UPLOAD_IMAGE_FOLDER_NAME,
                     'verify_unique': True,
                     'check_hamming': {'distance': 11, "time_frame": 15}})
        serializer.is_valid(raise_exception=True)
        return serializer

    def validate_url(self, value):
        for site in settings.UNSUPPORTED_UPLOAD_SITES:
            if site in value:
                raise ValidationError("Site not currently supported")
        return value

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
