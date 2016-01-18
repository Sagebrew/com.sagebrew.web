from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from neomodel import db

from sb_updates.neo_models import Update
from sb_updates.serializers import UpdateSerializer

from .neo_models import Quest


class QuestEpicSitemap(Sitemap):
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


class QuestUpdateSitemap(Sitemap):
    priority = 0.6
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        query = "MATCH (n:Quest)-[:CREATED_AN]->(update:Update)" \
                "WHERE n.active=true " \
                "RETURN update"
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Update.inflate(row[0]) for row in res]

    def location(self, obj):
        return UpdateSerializer(obj).data['url']
