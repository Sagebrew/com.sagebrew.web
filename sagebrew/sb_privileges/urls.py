from django.conf.urls import url, patterns

from .views import (create_privilege, CreatePrivilege)

urlpatterns = patterns(
    'sb_privileges.views',
    url(r'^create/privilege/', CreatePrivilege.as_view()),
    url(r'^create/', create_privilege, name="create_privilege"),
)
