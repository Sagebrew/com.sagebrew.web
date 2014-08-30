from neomodel import (StructuredNode, DateTimeProperty, IntegerProperty,
                      JSONProperty)

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