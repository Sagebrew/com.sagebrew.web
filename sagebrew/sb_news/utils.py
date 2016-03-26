# -*- coding: utf8 -*-
from __future__ import print_function
import unicodedata as ud
from uuid import uuid1
import io
import pytz
import urllib2
from itertools import chain
import requests
from bs4 import BeautifulSoup
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from json import load
import icu

from time import sleep
from logging import getLogger
from dateutil import parser
from datetime import datetime, timedelta
from difflib import SequenceMatcher

from django.conf import settings

from rest_framework.exceptions import ValidationError

from neomodel import DoesNotExist, db

from api.utils import generate_summary
from sb_uploads.serializers import UploadSerializer
from sb_uploads.utils import get_image_data, hamming_distance
from .neo_models import NewsArticle

logger = getLogger("loggly_logs")


def is_latin(uchr):
    latin_letters = {}
    try:
        return latin_letters[uchr]
    except KeyError:
        return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))


def only_roman_chars(unistr):
    return all(is_latin(uchr)
               for uchr in unistr
               if uchr.isalpha())


def find_news(limit_offset_fxn, count_query, link_objects_callback):
    requests_left = 26
    skip = 0
    limit = 25
    res, _ = db.cypher_query(count_query)
    total = res.one
    while requests_left > limit:
        news_objects = limit_offset_fxn(skip, limit)
        link_objects_callback(news_objects)
        if skip >= total:
            break
        skip += limit
        sleep(5)
    return True


def gather_news_results(query):
    payload = {
        "token": settings.WEBHOSE_KEY,
        "format": "json",
        "q": query,
    }
    query = "https://webhose.io/search"
    if not settings.DEBUG:
        response = requests.get(query, params=payload,
                                headers={"Accept": "text/plain"},
                                timeout=60)
        try:
            results = response.json()
        except ValueError as exc:
            logger.exception(exc)
            logger.critical(response.text)
            return None
    else:
        with open(settings.PROJECT_DIR + '/sb_news/tests/test.json') \
                as data_file:
            results = {"posts": list(chain.from_iterable(
                [result['posts'] for result in load(data_file)])),
                "requestsLeft": 0}
            for published in results['posts']:
                published['thread']['published'] = str(datetime.now(pytz.utc))
                published['published'] = str(datetime.now(pytz.utc))
    return results


def get_reformed_url(url):
    if settings.WEBHOSE_FREE:
        intermediate_page = requests.get(url)
        soup = BeautifulSoup(intermediate_page.text)
        for script in soup.find_all('script'):
            index_value = str(script).find('window.location.href')
            chop_string = str(
                script)[index_value + len('window.location.href="'):]
            url = str(chop_string)[:chop_string.find('"')]
    return url


def get_internal_image(main_image):
    object_uuid = str(uuid1())
    if main_image == "" or main_image is None \
            or "sponsored" in main_image:
        raise ValidationError("Invalid URL")

    try:
        file_object = urllib2.urlopen(main_image)
    except (ValueError, urllib2.HTTPError, urllib2.URLError):
        raise ValidationError("Invalid URL")
    read_file = file_object.read()
    file_size = len(read_file)
    http_message = file_object.info()
    load_file = io.BytesIO(read_file)
    file_format = http_message.type.split('/')[1]
    width, height, file_name, image = get_image_data(
        object_uuid, load_file)

    serializer = UploadSerializer(data={
        "file_size": file_size,
        "file_format": file_format,
    })
    if serializer.is_valid():
        upload = serializer.save(
            width=width, height=height, file_name=file_name,
            object_uuid=object_uuid,
            file_object=read_file,
            verify_unique=True,
            image=image,
            folder=settings.AWS_UPLOAD_IMAGE_FOLDER_NAME,
        )
    else:
        raise ValidationError("Invalid Input")

    return upload


def verify_not_excluded_article(title):
    for excluded_article in settings.DEFAULT_EXCLUDE_ARTICLES:
        # If the title has something similar to an article
        # we don't want to include, remove it
        # Not a list comprehension to ease readability. Not a
        # huge issue since this is normally called in a task.
        if SequenceMatcher(
                a=excluded_article.lower(), b=title.lower()).ratio() > .70:
            raise ValidationError("Title Has Set Excluded Content")


def verify_uniqueness(title, main_image, url, content):
    # Get news articles with close titles, exact titles, or
    # the same main image
    if title[0] == '"' or title[0] == "'":
        title = title[1:]
    if title[:len(title)] == '"' or title[:len(title)] == "'":
        title = title[:len(title) - 1]
    query = """
        MATCH (news:NewsArticle)
        WHERE (news.title =~ "(?i).*%s.*" ) OR
        news.main_image = "%s"
        RETURN news""" % (title, main_image)
    res, _ = db.cypher_query(query)
    for row in res:
        # Check if they go to the same page
        current_url = urlparse(url)
        compare_url = urlparse(row[0]['url'])
        if current_url.path == compare_url.path \
                and current_url.netloc == compare_url.netloc:
            raise ValidationError("Same URL Found")
        # Make sure we're not getting some explicit site through
        # the crawlers
        if [site for site in settings.EXPLICIT_STIES
                if site in current_url.netloc]:
            raise ValidationError("Explicit Content Found")
        # Check how close the titles are together
        title_closeness = SequenceMatcher(
            a=row[0]['title'], b=title).ratio()
        # Check how close the content is to each other
        content_closeness = SequenceMatcher(
            a=row[0]['content'], b=content).ratio()
        if title_closeness > 0.83 or content_closeness > 0.85:
            raise ValidationError("Title Too Close to Existing Content")
        # See if they share an image
        if row[0]['main_image'] == main_image:
            # If they share the same image could still be
            # different stories but since we don't want to show
            # the same image twice on a feed lets be more strict
            # on how different they need to be
            if title_closeness > 0.65 or content_closeness > 0.65:
                raise ValidationError("Title Too Close to Existing Content")

    return title


def verify_unique_title(title):
    query = 'MATCH (news:NewsArticle) ' \
            'WHERE news.title = "%s" RETURN news' % title
    res, _ = db.cypher_query(query)
    if res.one is not None:
        raise ValidationError("Found Same Title or Image")
    return True


def verify_unique_content(content, summary):
    if summary.strip() == "" or summary is None:
        raise ValidationError("Summary cannot be empty")
    skip = 0
    while True:
        query = 'MATCH (news:NewsArticle) RETURN news ' \
                'SKIP %s LIMIT 25' % skip
        skip += 24
        res, _ = db.cypher_query(query)
        if not res.one:
            break
        for row in res:
            content_closeness = SequenceMatcher(
                a=row[0]['content'], b=content).ratio()
            if content_closeness > 0.65:
                raise ValidationError("Content is too close to another article")
            summary_closeness = SequenceMatcher(
                a=row[0]['summary'], b=summary
            )
            if summary_closeness > 0.65:
                raise ValidationError("Summary is too close to another article")
    return True


def verify_unique_images(image_hash):
    skip = 0
    then = (datetime.now(pytz.utc) - timedelta(days=15)).strftime("%s")
    while True:
        query = 'MATCH (news:NewsArticle)-[:IMAGE_ON_PAGE]->' \
                '(image:UploadedObject) WHERE image.created > %s ' \
                'RETURN image.image_hash ' \
                'SKIP %s LIMIT 100' % (then, skip)
        skip += 99
        res, _ = db.cypher_query(query)
        if not res.one:
            break
        for row in res:
            result = hamming_distance(row[0], str(image_hash))
            if result < 11:
                raise ValidationError("Images too close to existing images")
    return True


def verify_supported_domain(compare_domain):
    for site in settings.UNSUPPORTED_UPLOAD_SITES:
        if site in compare_domain:
            raise ValidationError("Site not currently supported")
    return True


def query_provider(query):
    results = gather_news_results(query)
    articles = []
    for post in results['posts']:
        if only_roman_chars(post['title']):
            thread = post.pop('thread', None)
            highlight_text = post.pop('highlightText', None)
            highlight_title = post.pop('highlightTitle', None)
            external_id = post.pop('uuid', None)
            content = post.pop('text', None)
            post.pop('ord_in_thread', None)
            thread.pop('published', None)
            crawled = parser.parse(post.pop('crawled', None))
            published = parser.parse(post.pop('published', None))
            url = post.pop('url', None)
            url = get_reformed_url(url)
            try:
                upload = get_internal_image(thread.pop('main_image'))
                main_image = upload.url
            except ValidationError as e:
                continue
            if thread['spam_score'] < 0.3:
                # We currently don't have a way to support guardian images
                # so skip this
                try:
                    verify_supported_domain(thread['site_full'])
                except ValidationError:
                    continue
                try:
                    NewsArticle.nodes.get(external_id=external_id)
                except (NewsArticle.DoesNotExist, DoesNotExist):
                    # Need to use this rather than .title() because .title()
                    # does not handle things like "Wouldn't" properly. It
                    # converts it to "Wouldn'T" rather than keeping the T
                    # lowercase
                    title = post['title'].replace('"', "").strip()
                    en_us_locale = icu.Locale('en_US')
                    break_iter = icu.BreakIterator.createWordInstance(
                        en_us_locale)
                    temp_title = icu.UnicodeString(title)
                    title = unicode(temp_title.toTitle(
                        break_iter, en_us_locale))
                    try:
                        verify_not_excluded_article(title)
                        post.pop('title', None)
                    except ValidationError:
                        continue
                    try:
                        summary = generate_summary(content)
                        title = verify_uniqueness(title, main_image, url,
                                                  content)
                        verify_unique_title(title)
                        verify_unique_content(content, summary)
                        verify_unique_images(upload.image_hash)
                    except(ValidationError, ValueError):
                        continue
                    article = NewsArticle(
                        external_id=external_id,
                        url=url,
                        title=title,
                        highlight_text=highlight_text,
                        highlight_title=highlight_title,
                        content=content, site_full=thread['site_full'],
                        site=thread['site'],
                        site_section=['site_section'],
                        section_title=thread['section_title'],
                        replies_count=thread['replies_count'],
                        participants_count=thread['participants_count'],
                        site_type=thread['site_type'],
                        country=thread['country'],
                        spam_score=thread['spam_score'],
                        main_image=main_image,
                        performance_score=thread['performance_score'],
                        crawled=crawled, published=published,
                        summary=summary,
                        **post).save()
                    article.images.connect(upload)
                    articles.append(article)
    return articles, results['requestsLeft']


def tag_callback(news_objects):
    for tag in news_objects:
        query = '"%s political" language:(english) thread.country:US ' \
                'performance_score:>8 (site_type:news)' % tag.name
        articles, requests_left = query_provider(query)
        [article.tags.connect(tag) for article in articles]
    return True
