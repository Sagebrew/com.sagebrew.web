import pytz
from datetime import datetime

from neomodel import (BooleanProperty, DateTimeProperty, StringProperty,
                      StructuredNode, IntegerProperty, Relationship,
                      StructuredRel, JSONProperty, FloatProperty,
                      RelationshipTo)

class SearchQuery(StructuredNode):
    weight = IntegerProperty(default=0)
    query = StringProperty(unique_index=True)
    times_searched = IntegerProperty(default=1)
    last_searched = DateTimeProperty(default=datetime.now(pytz.utc))
    trending = BooleanProperty(default=False)

    #relationships
    trending_weights = RelationshipTo('TrendingWeight', 'TRENDING_WEIGHT')
    searched_by = Relationship('plebs.neo_modes.Pleb', 'SEARCHED_BY')
    keywords = Relationship(SearchCount, 'KEYWORDS', model=KeyWordRel)

class KeyWord(StructuredNode):
    keyword = StringProperty()
    weight = IntegerProperty(default=0)

class SearchCount(StructuredRel):
    times_searched = IntegerProperty(default=1)
    last_searched = DateTimeProperty(default=datetime.now(pytz.utc))

class KeyWordRel(StructuredRel):
    relevance = FloatProperty(default=0)

class TrendingWeight(StructuredNode):
    trending_start = DateTimeProperty()
    trending_end = DateTimeProperty()
    trending_hourly_weight = IntegerProperty(default=0)
    trending_daily_weight = IntegerProperty(default=0)
    trending_weekly_weight = JSONProperty(default={"day0": 0, "day1": 0,
                                                   "day2": 0, "day3": 0,
                                                   "day4": 0, "day5": 0,
                                                   "day6": 0})
    trending_monthly_weight = JSONProperty(default={"week0": 0, "week1": 0,
                                                    "week2": 0, "week3": 0})
    trending_yearly_weight = JSONProperty(default={"month0": 0, "month1": 0,
                                                   "month2": 0, "month3": 0,
                                                   "month4": 0, "month5": 0,
                                                   "month6": 0, "month7": 0,
                                                   "month8": 0, "month9": 0,
                                                   "month10": 0, "month11": 0,})

