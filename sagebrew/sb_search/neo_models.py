from django.conf import settings

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

    def get_labels(self):
        query = 'START n=node(%d) RETURN DISTINCT labels(n)' % (self._id)
        res, col = db.cypher_query(query)
        return res[0][0]

    def get_child_label(self):
        """
        With the current setup the actual piece of content is the last
        label.

        This goes on the assumption that Neo4J returns labels in order of
        assignment. Since neomodel assigns these in order of inheritance
        the top most parent being first and the bottom child being last
        we assume that our actual real commentable object is last.

        This can be accomplished by ensuring that the content is the
        bottom most child in the hierarchy. Currently this is only used for
        determining what content a comment is actually associated with for
        url linking. The commented out logic below can be substituted if with
        a few additional items if this begins to not work

            def get_child_labels(self):
                parents = inspect.getmro(self.__class__)
                # Creates a generator that enables us to access all the
                # names of the parent classes
                parent_array = (o.__name__ for o in parents)
                child_array = list(set(self.get_labels()) - set(parent_array))
                return child_array

            def get_child_label(self):
                labels = self.get_labels()
                # If you want to comment on something the class name must be
                # listed here
                content = ['Post', 'Question', 'Solution']
                try:
                    set(labels).intersection(content).pop()
                except KeyError:
                    return ""

        :return:
        """
        return list(set(self.get_labels()) - set(settings.REMOVE_CLASSES))[0]
