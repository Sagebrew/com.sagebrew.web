# -*- coding: utf8 -*-
import re
import unicodedata as ud
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse

from time import sleep
from logging import getLogger
from dateutil import parser
from difflib import SequenceMatcher


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
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

    language = 'english'
    sentence_count = 7
    summary_length = 250
    time_exp = re.compile(
        r'(1[012]|[1-9]):[0-5][0-9](\\s)?(?i)\s?(am|pm|AM|PM)')
    exclude_sentences = ["Story highlights", ]
    stemmer = Stemmer(language)
    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)
    articles = []
    payload = {
        "token": settings.WEBHOSE_KEY,
        "format": "json",
        "q": query,
    }
    query = "https://webhose.io/search"
    # TODO in development mode get info from file not pinging server so we
    # don't use all our api tokens
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
            url = post.pop('url', None)
            if settings.WEBHOSE_FREE:
                intermediate_page = requests.get(url)
                soup = BeautifulSoup(intermediate_page.text)
                for script in soup.find_all('script'):
                    index_value = str(script).find('window.location.href')
                    chop_string = str(
                        script)[index_value + len('window.location.href="'):]
                    url = str(chop_string)[:chop_string.find('"')]
            logger.critical(thread)
            logger.critical(post)
            if thread['spam_score'] < 0.5:
                if thread['main_image'] == "" or thread['main_image'] is None:
                    continue
                try:
                    NewsArticle.nodes.get(external_id=external_id)
                except (NewsArticle.DoesNotExist, DoesNotExist):
                    # Get news articles with close titles, exact titles, or
                    # the same main image
                    query = 'MATCH (news:NewsArticle) ' \
                            'WHERE (news.title =~ "(?i).*%s.*" ) OR ' \
                            'news.title = "%s" OR news.main_image = "%s" ' \
                            'RETURN news' % (post['title'], post['title'],
                                             thread['main_image'])
                    res, _ = db.cypher_query(query)
                    for row in res:
                        # Check if they go to the same page
                        current_url = urlparse(url)
                        compare_url = urlparse(row[0]['url'])
                        if current_url.path == compare_url.path\
                                and current_url.netloc == compare_url.netloc:
                            break
                        # Make sure we're not getting some explicit site through
                        # the crawlers
                        if [site for site in settings.EXPLICIT_STIES
                                if site in current_url.netloc]:
                            break
                        # Check how close the titles are together
                        title_closeness = SequenceMatcher(
                            a=row[0]['title'], b=post['title']).ratio()
                        # Check how close the content is to each other
                        content_closeness = SequenceMatcher(
                            a=row[0]['content'], b=content).ratio()
                        if title_closeness > 0.83 or content_closeness > 0.85:
                            break
                        # See if they share an image
                        if row[0]['main_image'] == thread['main_image']:
                            # If they share the same image could still be
                            # different stories but since we don't want to show
                            # the same image twice on a feed lets be more strict
                            # on how different they need to be
                            if title_closeness > 0.65 or \
                                    content_closeness > 0.65:
                                break
                    else:
                        # If we get through the for loop without finding an
                        # article too similar to the proposed article then
                        # lets save it off
                        article = NewsArticle(
                            external_id=external_id,
                            url=url,
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
                        summary = ""
                        sentence_list = [
                            unicode(sentence) for sentence in summarizer(
                                PlaintextParser.from_string(
                                    article.content.encode(
                                        'utf-8').strip().decode('utf-8'),
                                    Tokenizer(language)).document,
                                sentence_count)]
                        for sentence in sentence_list:
                            excluded = [exclude for exclude in exclude_sentences
                                        if exclude in sentence]
                            if time_exp.search(sentence) is None \
                                    and len(summary) < summary_length \
                                    and not excluded:
                                summary += " " + sentence
                        article.summary = summary
                        article.save()
                        articles.append(article)
    return articles, results['requestsLeft']


def tag_callback(news_objects):
    for tag in news_objects:
        query = '"%s" language:(english) thread.country:US ' \
                'performance_score:>8 (site_type:news)' % tag.name
        articles, requests_left = query_webhose(query)
        [article.tags.connect(tag) for article in articles]
    return True
