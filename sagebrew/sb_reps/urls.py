from django.conf.urls import url, patterns

from .views import (representative_page, get_experience_form, get_policy_form,
                    get_rep_info, get_education_form, get_bio_form,
                    get_goal_form)

urlpatterns = patterns(
    'sb_reps.views',
    url(r'^experience/$', get_experience_form, name="experience"),
    url(r'^policy/$', get_policy_form, name="policy"),
    url(r'^get_info/$', get_rep_info, name="rep_info"),
    url(r'^education/$', get_education_form, name="education"),
    url(r'^bio/$', get_bio_form, name="bio"),
    url(r'^goals/$', get_goal_form, name="goal"),
    url(r'^(?P<rep_type>[A-Za-z0-9.@_%+-]{7,60})/(?P<rep_id>[A-Za-z0-9.@_%+-]{7,60})/$', representative_page,
        name="rep_page")
    )