from django.conf.urls import patterns, url

from .views import (save_question_view, edit_question_view,
                    delete_question_view, close_question_view,
                    get_question_view, vote_question_view,
                    submit_question_view_page, question_page,
                    question_detail_page)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^$', question_page, name='question_page'),
    url(r'^submit_question/$', submit_question_view_page, name='save_question_page'),
    url(r'^submit_question_api/$', save_question_view, name='save_question'),
    url(r'^query_questions_api/$', get_question_view, name='get_questions'),
    url(r'^edit_question_api/$', edit_question_view, name='edit_question'),
    url(r'^delete_question_api/$', delete_question_view, name='delete_question'),
    url(r'^vote_question_api/$', vote_question_view, name='vote_question'),
    url(r'^close_question_api/$', close_question_view, name='close_question'),
    url(r'^(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/$', question_detail_page, name='question_detail_page'),
)