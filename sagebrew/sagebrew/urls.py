from django.conf.urls import patterns, include
from django.conf import settings
from django.http import HttpResponse
from django.contrib import admin
from django.views.generic.base import RedirectView, TemplateView


admin.autodiscover()

urlpatterns = patterns('',
    (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /",
                                              mimetype="text/plain")),
    (r'^favicon\.ico$', RedirectView.as_view(
                                        url='/static/images/favicon.ico')),
    (r'^admin/', include('admin_honeypot.urls')),
    (r'^secret/', include(admin.site.urls)),
    (r'^$', TemplateView.as_view(template_name="index.html")),
    (r'^locations/$', TemplateView.as_view(template_name="location.html")),
    (r'^contact_us/$', TemplateView.as_view(template_name="contact_us.html")),
    (r'^accounts/', include('allauth.urls')),
    (r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    (r'^api/', include('friends.api_urls')),
    (r'^user_profiles/', include('user_profiles.urls')),
)

if settings.DEBUG :
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
                {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
