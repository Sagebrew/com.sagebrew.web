import pytz
from datetime import datetime

from neomodel import (BooleanProperty, DateTimeProperty, StringProperty,
                      StructuredNode, IntegerProperty, Relationship,
                      StructuredRel, FloatProperty, RelationshipTo)


class ResultClickedRel(StructuredRel):
    date_clicked = DateTimeProperty()


class KeyWordRel(StructuredRel):
    relevance = FloatProperty(default=0)


class SearchResult(StructuredNode):
    result_id = StringProperty(unique_index=True)
    object_type = StringProperty()
    object_uuid = StringProperty()

    #relationships
    queries = RelationshipTo('sb_search.neo_models.SearchQuery', 'QUERY')
    clicked_by = RelationshipTo('plebs.neo_models.Pleb', 'CLICKED_BY',
                                model=ResultClickedRel)


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
    searched_by = Relationship('plebs.neo_models.Pleb', 'SEARCHED_BY')
    keywords = RelationshipTo(KeyWord, 'KEYWORDS', model=KeyWordRel)
    results = RelationshipTo(SearchResult, 'RESULT')





