from django.conf.urls import patterns, url

from .views import CouncilView

urlpatterns = patterns(
    'sb_council.views',
    url(r'^$', CouncilView.as_view(template_name="council_page.html"),
        name='council_page'),

    # positions
    url(r'^positions/$',
        CouncilView.as_view(template_name="council_positions.html"),
        name='council_positions'),
    url(r'^positions/verified/$',
        CouncilView.as_view(template_name="council_positions.html"),
        name='council_positions_verified'),
    url(r'^positions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/edit/$',
        CouncilView.as_view(template_name="council_position_edit.html"),
        name='council_positions_edit'),

    # missions
    url(r'^missions/$',
        CouncilView.as_view(template_name="council/missions.html"),
        name='council_missions'),
    url(r'^missions/reviewed/$',
        CouncilView.as_view(template_name="council/missions.html"),
        name='council_missions_reviewed'),
    url(r'^missions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/review/$',
        CouncilView.as_view(template_name="council/missions_review.html"),
        name='council_missions_review')
)
