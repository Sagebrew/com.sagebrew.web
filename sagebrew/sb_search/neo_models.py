from neomodel import (BooleanProperty, DateTimeProperty, StringProperty,
                      StructuredNode, IntegerProperty, Relationship,
                      StructuredRel, FloatProperty, RelationshipTo, db)

from api.neo_models import SBObject, get_current_time


class Impression(StructuredRel):
    viewed_at = DateTimeProperty(default=get_current_time)
    times_viewed = IntegerProperty(default=0)


class ResultClickedRel(StructuredRel):
    date_clicked = DateTimeProperty()


class KeyWordRel(StructuredRel):
    relevance = FloatProperty(default=0)


class SearchResult(SBObject):
    result_id = StringProperty(unique_index=True)
    object_type = StringProperty()

    # relationships
    queries = RelationshipTo('sb_search.neo_models.SearchQuery', 'QUERY')
    clicked_by = RelationshipTo('plebs.neo_models.Pleb', 'CLICKED_BY',
                                model=ResultClickedRel)


class KeyWord(StructuredNode):
    keyword = StringProperty()
    weight = IntegerProperty(default=0)

    # relationships
    search_queries = RelationshipTo('sb_search.neo_models.SearchQuery',
                                    'SEARCH_QUERY')


class SearchQuery(StructuredNode):
    weight = IntegerProperty(default=0)
    search_query = StringProperty(unique_index=True)
    times_searched = IntegerProperty(default=1)
    last_searched = DateTimeProperty(default=get_current_time)
    trending = BooleanProperty(default=False)

    # relationships
    searched_by = Relationship('plebs.neo_models.Pleb', 'SEARCHED_BY')
    keywords = RelationshipTo(KeyWord, 'KEYWORDS', model=KeyWordRel)
    results = RelationshipTo(SearchResult, 'RESULT')


class Searchable(SBObject):
    search_id = StringProperty()
    populated_es_index = BooleanProperty(default=False)
    view_count = IntegerProperty(default=0)

    # relationships
    viewed_by = RelationshipTo('plebs.neo_models.Pleb', "VIEWED_BY",
                               model=Impression)

    def get_view_count(self):
        return self.view_count

    def increment_view_count(self):
        try:
            # This is to ensure the number doesn't cross into a BigInteger
            # which our current setup does not support. If views get over a
            # billion we probably can just mark it as "a lot" as more than that
            # is probably only useful for internal analysis or sorting/trending
            # which are probably better analyzed on a week/day basis than
            # overall anyways.
            if self.view_count >= 4611686018427387900:
                return 4611686018427387900
            self.view_count += 1
            self.save()
            return self.view_count
        except IndexError:
            return 0
