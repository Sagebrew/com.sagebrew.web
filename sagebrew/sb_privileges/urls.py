from django.conf.urls import url, patterns

from .views import (check_action, create_privilege, CreateAction,
                    CreateRequirement, CreatePrivilege)

urlpatterns = patterns(
    'sb_privileges.views',
    url(r'^check/action/', check_action, name="check_action"),
    url(r'^create/privilege/', CreatePrivilege.as_view()),
    url(r'^create/action/', CreateAction.as_view()),
    url(r'^create/requirement/', CreateRequirement.as_view()),
    url(r'^create/', create_privilege, name="create_privilege"),
)