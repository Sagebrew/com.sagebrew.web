from django.conf.urls import patterns, include
from django.conf import settings
from django.http import HttpResponse
from django.contrib import admin
from django.views.generic.base import RedirectView, TemplateView
from django.conf.urls import patterns, url

admin.autodiscover()

urlpatterns = patterns('',
    (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /",
                                              mimetype="text/plain")),
    (r'^favicon\.ico$', RedirectView.as_view(
                                        url='/static/images/favicon.ico')),
    (r'^admin/', include('admin_honeypot.urls')),
    (r'^secret/', include(admin.site.urls)),
    (r'^$', TemplateView.as_view(template_name="index.html")),
    (r'^accounts/', include('allauth.urls')),
    (r'^locations/$', TemplateView.as_view(template_name="location.html")),
    url(r'^404/$', TemplateView.as_view(template_name="404.html"),
        name="404_Error"),
    (r'^contact_us/$', TemplateView.as_view(template_name="contact_us.html")),
    (r'^accounts/', include('allauth.urls')),
    (r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    (r'^api/', include('plebs.api_urls')),
    (r'^user_profiles/', include('user_profiles.urls')),
    (r'^registration/', include('sb_registration.urls')),
    (r'^comments/', include('sb_comments.urls')),
    (r'^posts/', include('sb_posts.urls')),
    (r'^notifications/', include('sb_notifications.urls'))
)

if settings.DEBUG :
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
