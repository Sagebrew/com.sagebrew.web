from django.conf.urls import patterns, url

from .views import CouncilView

urlpatterns = patterns(
    'sb_council.views',
    url(r'^$', CouncilView.as_view(template_name="council_page.html"),
        name='council_page'),
    url(r'^positions/$',
        CouncilView.as_view(template_name="council_positions.html"),
        name='council_positions'),
    url(r'^positions/verified/$',
        CouncilView.as_view(template_name="council_positions.html"),
        name='council_positions_verified'),
    url(r'^positions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/edit/$',
        CouncilView.as_view(template_name="council_position_edit.html"),
        name='council_positions_edit')
)
