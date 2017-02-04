from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from neomodel import db

from .neo_models import Question


class QuestionSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        query = "MATCH (n:Question) WHERE n.to_be_deleted=false RETURN n"
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Question.inflate(row[0]) for row in res]

    def lastmod(self, obj):
        return obj.last_edited_on

    def location(self, obj):
        return obj.get_url()
