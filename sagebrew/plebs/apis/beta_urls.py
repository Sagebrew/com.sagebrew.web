from django.conf.urls import patterns, url

from plebs.views import ListBetaUsers, RetrieveBetaUsers, invite_beta_user

urlpatterns = patterns(
    'plebs.views',
    url(r'^betausers/$', ListBetaUsers.as_view(), name='betauser-list'),
    url(r'^betausers/(?P<email>[A-Za-z0-9.@_%+-]{1,90})/$',
        RetrieveBetaUsers.as_view(), name='betauser-detail'),
    url(r'^betausers/(?P<email>[A-Za-z0-9.@_%+-]{1,90})/invite/$',
        invite_beta_user, name="betauser-invite"),
)
