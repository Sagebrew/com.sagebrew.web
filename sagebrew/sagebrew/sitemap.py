from django.contrib import sitemaps
from django.core.urlresolvers import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['contact_us', 'terms_redirect']

    def location(self, item):
        return reverse(item)


class SignupSitemap(sitemaps.Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['signup']

    def location(self, item):
        return reverse(item)
