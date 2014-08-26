import pytz
from datetime import datetime

from neomodel import (BooleanProperty, DateTimeProperty, StringProperty,
                      StructuredNode, IntegerProperty, Relationship,
                      StructuredRel, JSONProperty, FloatProperty,
                      RelationshipTo)

class KeyWordRel(StructuredRel):
    relevance = FloatProperty(default=0)

class SearchCount(StructuredRel):
    times_searched = IntegerProperty(default=1)
    last_searched = DateTimeProperty(default=datetime.now(pytz.utc))

class KeyWord(StructuredNode):
    keyword = StringProperty()
    weight = IntegerProperty(default=0)

    #relationships
    search_queries = RelationshipTo('sb_search.neo_models.SearchQuery',
                                    'SEARCH_QUERY')

class SearchQuery(StructuredNode):
    weight = IntegerProperty(default=0)
    search_query = StringProperty(unique_index=True)
    times_searched = IntegerProperty(default=1)
    last_searched = DateTimeProperty(default=datetime.now(pytz.utc))
    trending = BooleanProperty(default=False)

    #relationships
    trending_weights = RelationshipTo('sb_trends.neo_models.TrendingWeight', 'TRENDING_WEIGHT')
    searched_by = Relationship('plebs.neo_models.Pleb', 'SEARCHED_BY')
    keywords = RelationshipTo(KeyWord, 'KEYWORDS', model=KeyWordRel)





