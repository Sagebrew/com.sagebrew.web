from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from neomodel import db

from .neo_models import Quest


class QuestSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        query = "MATCH (n:Quest) WHERE n.active=true " \
                "RETURN n"
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Quest.inflate(row[0]) for row in res]

    def location(self, obj):
        return reverse('quest', kwargs={"username": obj.owner_username})
