from time import sleep
from logging import getLogger
import unicodedata as ud
from dateutil import parser
import requests

from django.conf import settings

from neomodel import DoesNotExist, db

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


def query_webhose(query):
    articles = []
    payload = {
        "token": settings.WEBHOSE_KEY,
        "format": "json",
        "q": query,
    }
    query = "https://webhose.io/search"
    response = requests.get(query, params=payload,
                            headers={"Accept": "text/plain"},
                            timeout=60)
    try:
        results = response.json()
    except ValueError as exc:
        logger.exception(exc)
        logger.critical(response.text)
        return None
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
            if thread['spam_score'] < 0.5:
                try:
                    NewsArticle.nodes.get(external_id=external_id)
                except (NewsArticle.DoesNotExist, DoesNotExist):
                    article = NewsArticle(
                        external_id=external_id,
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
                        main_image=thread['main_image'],
                        performance_score=thread['performance_score'],
                        crawled=crawled, published=published,
                        **post).save()
                    articles.append(article)
    return articles, results['requestsLeft']


def tag_callback(news_objects):
    for tag in news_objects:
        query = '"%s" language:(english) thread.country:US ' \
                'performance_score:>8 (site_type:news)' % tag.name
        articles, requests_left = query_webhose(query)
        [article.tags.connect(tag) for article in articles]
    return True