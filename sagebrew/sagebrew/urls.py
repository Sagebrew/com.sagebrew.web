from django.conf.urls import patterns, include
from django.http import HttpResponse
from django.contrib import admin
from django.views.generic.base import RedirectView


admin.autodiscover()

urlpatterns = patterns('',
    (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /",
                                              mimetype="text/plain")),
    (r'^favicon\.ico$', RedirectView.as_view(
                                        url='/static/images/favicon.ico')),
    (r'^admin/', include('admin_honeypot.urls')),
    (r'^secret/', include(admin.site.urls)),
)
