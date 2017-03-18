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

from neomodel import db

from .serializers import NewsArticleSerializer

logger = getLogger("loggly_logs")


def find_news(limit_offset_fxn, count_query, link_objects_callback):
    requests_left = settings.WEBHOSE_REQUEST_LIMIT + 1
    skip = 0
    limit = 25
    res, _ = db.cypher_query(count_query)
    total = res[0][0] if res else None
    while requests_left > limit and \
            requests_left > settings.WEBHOSE_REQUEST_LIMIT:
        news_objects = limit_offset_fxn(skip, limit)
        requests_left = link_objects_callback(news_objects)
        if skip >= total:
            break
        skip += limit
        sleep(5)
    return True


def gather_news_results(query, demo_file=None):
    payload = {
        "token": settings.WEBHOSE_KEY,
        "format": "json",
        "q": query,
    }
    url = "https://webhose.io/search"
    if settings.DEBUG:
        if demo_file is None:
            demo_file = settings.PROJECT_DIR + '/sb_news/tests/short_test.json'
        with open(demo_file) as data_file:
            file_info = load(data_file)
            try:
                results = {"posts": list(chain.from_iterable(
                    [result['posts'] for result in file_info])),
                    "requestsLeft": 0}
            except KeyError:
                results = {"posts": file_info, "requestsLeft": 0}
        for published in results['posts']:
            published['thread']['published'] = str(datetime.now(pytz.utc))
            published['published'] = str(datetime.now(pytz.utc))
    else:  # pragma: no cover
        # We have tested this in development and it works. But since webhose
        # has no test API keys and all queries are billable we need to avoid
        # triggering this in dev and testing. - Devon Bleibtrey
        response = requests.get(url, params=payload,
                                headers={"Accept": "text/plain"},
                                timeout=60, verify=False)
        try:
            results = response.json()
        except ValueError as exc:
            logger.exception(exc)
            return None
    return results


def get_reformed_url(url):
    if settings.WEBHOSE_FREE:
        if "omgili.com" not in url:
            return url
        intermediate_page = requests.get(url)
        soup = BeautifulSoup(intermediate_page.text, 'html.parser')
        for script in soup.find_all('script'):
            index_value = str(script).find('window.location.href')
            chop_string = str(
                script)[index_value + len('window.location.href="'):]
            url = str(chop_string)[:chop_string.find('"')]
    return url


def query_webhose(results, tag):
    for post in results['posts']:
        thread = post.pop('thread', None)
        if thread['spam_score'] < 0.3:
            external_id = post.pop('uuid', None)
            post.pop('ord_in_thread', None)
            thread.pop('published', None)
            published = parser.parse(post.pop('published', None))
            post["external_id"] = external_id
            post["url"] = get_reformed_url(post.pop('url', None))
            post['title_full'] = thread['title_full']
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
            post["image"] = thread.pop('main_image')
            post["performance_score"] = thread['performance_score']
            post["crawled"] = parser.parse(post.pop('crawled', None))
            post["published"] = published
            post["provider"] = "webhose"
            post['language'] = "en"
            serializer = NewsArticleSerializer(data=post)
            if serializer.is_valid():
                article = serializer.save()
            else:
                logger.critical(serializer.errors)
                continue
            article.tags.connect(tag)
    return results['requestsLeft']


def tag_callback(news_objects):
    requests_left = 0
    for tag in news_objects:
        query = '%s politics language:(english) thread.country:US ' \
                'performance_score:>9 (site_type:news)' % (
                    tag.name.replace('-', " ").replace('_', " "))
        results = gather_news_results(query)
        requests_left = query_webhose(results, tag)
    return requests_left
