from django.conf.urls import patterns, url

from .views import (profile_page, get_user_search_view,
                    about_page, friends_page,
                    reputation_page, get_user_rep, get_user_questions,
                    get_user_conversation, get_user_age)


urlpatterns = patterns(
    'plebs.views',
    url(r'^v1/profile/conversation/', get_user_conversation,
        name="user_conversation_api"),
    url(r'^v1/profile/question/', get_user_questions,
        name="user_question_api"),
    url(r'^v1/profile/', get_user_rep, name="user_rep_api"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/about/',
       about_page, name="about_page"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/friends/',
       friends_page, name="friends_page"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/reputation/',
       reputation_page, name="reputation_page"),
    url(r'^search/(?P<pleb_email>[A-Za-z0-9.@_%+-]{1,150})',
        get_user_search_view, name="get_user_search_view"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/',
       profile_page, name="profile_page")

)