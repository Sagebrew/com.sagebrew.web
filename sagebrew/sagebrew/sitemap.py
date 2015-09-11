from django.contrib import sitemaps
from django.core.urlresolvers import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.4
    changefreq = 'never'
    protocol = 'https'

    def items(self):
        return ['contact_us', 'reset_password_page', 'login', 'logout']

    def location(self, item):
        return reverse(item)


class SignupSitemap(sitemaps.Sitemap):
    priority = 1.0
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['signup']

    def location(self, item):
        return reverse(item)
