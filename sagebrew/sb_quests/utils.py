from neomodel import db

from sb_news.utils import query_webhose

from sb_quests.neo_models import Quest


def limit_offset_query(skip, limit):
    query = 'MATCH (quest:Quest) ' \
            'RETURN tag SKIP %s LIMIT %s' % (skip, limit)
    res, _ = db.cypher_query(query)
    return [Quest.inflate(row[0]) for row in res]


def quest_callback(news_objects):
    for quest in news_objects:
        if quest.title is None:
            query = '"%s %s" language:(english) thread.country:US ' \
                    'performance_score:>8 (site_type:news)' % (quest.first_name,
                                                               quest.last_name)
        else:
            query = '"%s" language:(english) thread.country:US ' \
                    'performance_score:>8 (site_type:news)' % quest.title
        articles, requests_left = query_webhose(query)
        [quest.news_articles.connect(article) for article in articles]