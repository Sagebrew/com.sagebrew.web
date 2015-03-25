from django.conf.urls import patterns, url

from .views import (saga, about, updates, get_experience_form,
                    get_rep_info, get_bio_form, get_goal_form)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,30})/$', saga,
        name='action_saga'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,30})/about/$', about,
        name='action_about'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,30})/updates/', updates,
        name='action_updates'),
    url(r'^experience/$', get_experience_form, name="experience"),
    url(r'^get_info/$', get_rep_info, name="rep_info"),
    url(r'^bio/$', get_bio_form, name="bio"),
    url(r'^goals/$', get_goal_form, name="goal"),
)