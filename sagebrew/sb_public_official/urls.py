from django.conf.urls import patterns, url

from .views import (saga, about, updates, get_experience_form,
                    get_policy_form, get_rep_info, get_education_form,
                    get_bio_form, get_goal_form)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,30})/$', saga,
        name='action_saga'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,30})/about/$', about,
        name='action_about'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,30})/updates/', updates,
        name='action_updates'),

    url(r'^experience/$', get_experience_form, name="experience"),
    url(r'^policy/$', get_policy_form, name="policy"),
    url(r'^get_info/$', get_rep_info, name="rep_info"),
    url(r'^education/$', get_education_form, name="education"),
    url(r'^bio/$', get_bio_form, name="bio"),
    url(r'^goals/$', get_goal_form, name="goal"),
)