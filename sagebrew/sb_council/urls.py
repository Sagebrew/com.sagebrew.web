from django.conf.urls import url

from sagebrew.sb_council.views import CouncilView

urlpatterns = [
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
        name='council_missions_review'),

    # orders
    url(r'^orders/$',
        CouncilView.as_view(template_name="council/orders.html"),
        name='council_orders'),
    url(r'^orders/completed/$',
        CouncilView.as_view(template_name="council/orders.html"),
        name='council_orders_completed'),
    url(r'^orders/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/complete/$',
        CouncilView.as_view(template_name="council/order_complete.html"),
        name='council_orders_completion')
]
