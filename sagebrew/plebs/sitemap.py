from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from neomodel import db

from .neo_models import Pleb


class ProfileSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        query = "MATCH (n:Pleb) RETURN n"
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Pleb.inflate(row[0]) for row in res]

    def location(self, obj):
        return reverse('profile_page',
                       kwargs={"pleb_username": obj.username})
