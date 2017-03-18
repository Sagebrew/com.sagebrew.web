from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from neomodel import db

from sagebrew.sb_updates.neo_models import Update
from sagebrew.sb_updates.serializers import UpdateSerializer

from .neo_models import Mission


class MissionSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        query = "MATCH (n:Mission) WHERE n.active=true " \
                "RETURN DISTINCT n"
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Mission.inflate(row[0]) for row in res]

    def location(self, obj):
        return reverse('mission',
                       kwargs={'object_uuid': obj.object_uuid,
                               'slug': slugify(obj.get_mission_title())})


class MissionUpdateSitemap(Sitemap):
    priority = 0.6
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        query = "MATCH (n:Mission)<-[:ABOUT]-(update:Update)" \
                "WHERE n.active=true " \
                "RETURN update"
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Update.inflate(row[0]) for row in res]

    def location(self, obj):
        return UpdateSerializer(obj).data['url']


class MissionListSitemap(Sitemap):
        priority = 0.9
        changefreq = 'hourly'
        protocol = 'https'

        def items(self):
            return ['mission_list']

        def location(self, item):
            return reverse(item)
