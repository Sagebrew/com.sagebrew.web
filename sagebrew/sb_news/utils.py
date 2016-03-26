# -*- coding: utf8 -*-
from __future__ import print_function

import pytz

from itertools import chain
import requests
from bs4 import BeautifulSoup
from json import load

from time import sleep
from logging import getLogger
from dateutil import parser
from datetime import datetime

from django.conf import settings


from neomodel import DoesNotExist, db

from .serializers import NewsArticleSerializer
from .neo_models import NewsArticle

logger = getLogger("loggly_logs")


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


def query_provider(query):
    results = gather_news_results(query)
    articles = []
    for post in results['posts']:
        thread = post.pop('thread', None)
        if thread['spam_score'] < 0.3:
            external_id = post.pop('uuid', None)
            post.pop('ord_in_thread', None)
            thread.pop('published', None)
            published = parser.parse(post.pop('published', None))
            try:
                NewsArticle.nodes.get(external_id=external_id)
            except (NewsArticle.DoesNotExist, DoesNotExist):
                post["external_id"] = external_id
                post["url"] = get_reformed_url(post.pop('url', None))
                post["highlight_text"] = post.pop('highlightText', None)
                post["highlight_title"] = post.pop('highlightTitle', None)
                post["content"] = post.pop('text', None)
                post["site_full"] = thread['site_full']
                post["site"] = thread['site']
                post["site_section"] = thread['site_section']
                post["section_title"] = thread['section_title']
                post["replies_count"] = thread['replies_count']
                post["participants_count"] = thread['participants_count']
                post["site_type"] = thread['site_type']
                post["country"] = thread['country']
                post["spam_score"] = thread['spam_score']
                post["main_image"] = thread.pop('main_image')
                post["performance_score"] = thread['performance_score']
                post["crawled"] = parser.parse(post.pop('crawled', None))
                post["published"] = published
                post["provider"] = "webhose"
                serializer = NewsArticleSerializer(data=post)
                if serializer.is_valid():
                    article = serializer.save()
                else:
                    continue
                articles.append(article)
    return articles, results['requestsLeft']


def tag_callback(news_objects):
    for tag in news_objects:
        query = '"%s political" language:(english) thread.country:US ' \
                'performance_score:>8 (site_type:news)' % tag.name
        articles, requests_left = query_provider(query)
        [article.tags.connect(tag) for article in articles]
    return True
