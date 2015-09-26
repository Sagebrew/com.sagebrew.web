from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from neomodel import db

from .neo_models import PoliticalCampaign


class QuestEpicSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        query = "MATCH (n:PoliticalCampaign) WHERE n.active=true " \
                "RETURN n"
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [PoliticalCampaign.inflate(row[0]) for row in res]

    def location(self, obj):
        return reverse('quest_saga', kwargs={"username": obj.owner_username})


class QuestUpdateSitemap(Sitemap):
    priority = 0.6
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        query = "MATCH (n:PoliticalCampaign) WHERE n.active=true " \
                "RETURN n"
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [PoliticalCampaign.inflate(row[0]) for row in res]

    def location(self, obj):
        return reverse('quest_updates',
                       kwargs={"username": obj.owner_username})
