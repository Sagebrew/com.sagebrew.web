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
        return [PoliticalCampaign.inflate(row[0]) for row in res]

    def location(self, obj):
        return obj.get_url()


class QuestUpdateSitemap(Sitemap):
    priority = 0.6
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        query = "MATCH (n:PoliticalCampaign) WHERE n.active=true " \
                "RETURN n"
        res, _ = db.cypher_query(query)
        return [PoliticalCampaign.inflate(row[0]) for row in res]

    def location(self, item):
        return reverse('quest_updates',
                       kwargs={"username": item.owner_username})


class PublicOfficialSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        query = "MATCH (n:PoliticalCampaign) WHERE n.active=true " \
                "RETURN n"
        res, _ = db.cypher_query(query)
        return [PoliticalCampaign.inflate(row[0]) for row in res]

    def location(self, obj):
        return obj.get_url()